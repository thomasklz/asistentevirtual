import unittest

from knowledge import instructions, load_catalog, offline_reply


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def test_greeting(self):
        self.assertIn("Hola", offline_reply("hola", self.catalog))

    def test_fair_projects_are_out_of_scope(self):
        self.assertNotIn("proyectos", self.catalog)
        self.assertIn("solo respondo", offline_reply("¿Qué proyectos hay en la feria?", self.catalog))
        self.assertIn("solo respondo", offline_reply("¿Qué tecnologías usa la pizarra?", self.catalog))

    def test_unknown_fact_is_not_invented(self):
        self.assertIn("no tengo", offline_reply("¿A qué hora abre?", self.catalog).lower())

    def test_prompt_contains_catalog(self):
        self.assertIn("Computación", instructions(self.catalog))
        self.assertNotIn("Pizarra virtual", instructions(self.catalog))

    def test_current_curriculum(self):
        self.assertEqual("La carrera tiene 120 créditos.", offline_reply("¿Cuántos créditos tiene la carrera?", self.catalog))
        self.assertEqual("La carrera tiene 8 niveles.", offline_reply("¿Cuántos niveles tiene la carrera?", self.catalog))
        self.assertEqual("La carrera tiene 5760 horas.", offline_reply("¿Cuántas horas tiene la carrera?", self.catalog))
        self.assertEqual("La carrera tiene 41 asignaturas.", offline_reply("¿Cuántas materias tiene la carrera?", self.catalog))
        self.assertIn("Cálculo de una variable", offline_reply("¿Qué materias hay en primer nivel?", self.catalog))
        self.assertIn("Aprendizaje profundo", offline_reply("¿Qué hay en nivel 7?", self.catalog))

    def test_previous_curriculum_is_explicit(self):
        self.assertEqual("La malla anterior tenía 150 créditos.", offline_reply("¿Cuántos créditos tenía la malla anterior?", self.catalog))
        self.assertNotIn("150 créditos", offline_reply("¿Cómo es la malla de Computación?", self.catalog))

    def test_career_facts(self):
        self.assertIn("presencial", offline_reply("¿Cuál es la modalidad?", self.catalog))
        self.assertIn("Ingeniero/a", offline_reply("¿Qué título obtengo?", self.catalog))
        self.assertIn("432 horas", offline_reply("¿Cuántas horas de prácticas hay?", self.catalog))
        self.assertIn("algoritmos genéticos", offline_reply("¿Qué se estudia en Inteligencia artificial?", self.catalog))

    def test_ai_prompt_requests_only_asked_fact(self):
        self.assertIn("Da únicamente el dato solicitado", instructions(self.catalog))
        self.assertIn("desarrolla lo necesario", instructions(self.catalog))
        self.assertIn("es histórico", instructions(self.catalog))

    def test_greeting_does_not_hide_question(self):
        self.assertEqual("La carrera tiene 120 créditos.", offline_reply("Hola, ¿cuántos créditos tiene la carrera?", self.catalog))

    def test_new_career_details_are_specific(self):
        self.assertEqual("La carrera tiene 8 niveles.", offline_reply("¿Cuánto dura la carrera?", self.catalog))
        self.assertEqual("La jornada es diurna.", offline_reply("¿Cuál es la jornada?", self.catalog))
        self.assertEqual("El horario es de 08:00 a 17:00.", offline_reply("¿Cuál es el horario?", self.catalog))
        self.assertEqual("La jornada es diurna, de 08:00 a 17:00.", offline_reply("¿Cuál es la jornada y horario?", self.catalog))
        self.assertEqual("computacion@espam.edu.ec", offline_reply("¿Cuál es el correo de contacto?", self.catalog))
        self.assertEqual(self.catalog["carrera"]["mision"], offline_reply("¿Cuál es la misión?", self.catalog))
        self.assertEqual(self.catalog["carrera"]["vision"], offline_reply("¿Cuál es la visión?", self.catalog))
        self.assertEqual(self.catalog["carrera"]["objetivo"], offline_reply("¿Cuál es el objetivo?", self.catalog))
        self.assertEqual(self.catalog["carrera"]["perfil_egreso"], offline_reply("¿Cuál es el perfil de egreso?", self.catalog))
        self.assertIn("Gerente", offline_reply("¿Cuál es el campo profesional?", self.catalog))
        self.assertIn("Dirige proyectos", offline_reply("¿Qué hace un gerente de tecnología?", self.catalog))

    def test_historical_redesign_does_not_replace_current_duration(self):
        self.assertEqual("La carrera tiene 8 niveles.", offline_reply("¿Cuánto dura la carrera?", self.catalog))
        self.assertEqual("La malla anterior tenía 10 niveles.", offline_reply("¿Cuántos niveles tenía la malla anterior?", self.catalog))

    def test_teacher_lookup_by_subject(self):
        self.assertIn("Pinargote Bravo Víctor Joel", offline_reply("¿Quién dicta Aprendizaje automático?", self.catalog))
        self.assertIn("Toala Palma Diego Alexander", offline_reply("¿Quién da Base de datos?", self.catalog))
        self.assertIn("Loor Vera Alfonso Tomás", offline_reply("¿Quién dicta aplicaciones móviles?", self.catalog))

    def test_teacher_lookup_by_name_and_level(self):
        answer = offline_reply("¿Qué materias da Pinargote Bravo Víctor Joel?", self.catalog)
        self.assertIn("Aprendizaje automático (nivel 6)", answer)
        self.assertIn("Procesamiento de lenguaje natural (nivel 5)", answer)
        self.assertIn("Villao Loor María Belén", offline_reply("¿Qué docentes hay en 2do nivel?", self.catalog))

    def test_teacher_historical_levels_and_deduplication(self):
        answer = offline_reply("¿Qué asignaturas dicta Morales Carrillo Jessica Johanna?", self.catalog)
        self.assertIn("nivel 9, malla anterior", answer)
        self.assertIn("nivel 6", answer)
        self.assertEqual(answer.count("Gestión de proyectos tecnológicos (nivel 6)"), 1)
        self.assertIn("malla anterior", offline_reply("¿Qué docentes hay en 10mo nivel?", self.catalog))
        self.assertIn("malla anterior", offline_reply("¿Quién dicta Sistemas operativos II?", self.catalog))
        self.assertEqual("El listado proporcionado incluye 18 docentes.", offline_reply("¿Cuántos docentes hay?", self.catalog))
        all_teachers = offline_reply("Lista de docentes con materias y niveles", self.catalog)
        self.assertIn("Pinargote Bravo Víctor Joel: Aprendizaje automático (nivel 6)", all_teachers)

    def test_teacher_data_is_marked_as_undated(self):
        self.assertIn("fecha y período académico no indicados", self.catalog["docentes"]["fuente"])
        self.assertIn("no asegures que sigan vigentes", instructions(self.catalog))


if __name__ == "__main__":
    unittest.main()
