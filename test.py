from service import *
import unittest
from database import db, Positionnement, Affectuation, Status
import time


class UnitTests(unittest.TestCase):
    supermarket_mission = None
    jobsMission = None
    pablo = None
    felipe = None
    josie = None
    admin = None

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.josie = create_account_pour_ingenieur_etudes("josieposie", "password1", "Josie")
        self.felipe = create_account_pour_ingenieur_etudes("felipemaple", "password2", "Felipe")
        self.pablo = create_account_pour_ingenieur_etudes("pabloingles", "password3", "Pablo")
        self.admin = create_account_pour_ingenieur_affaires("adminaccount", "password4", "Admin")

        self.supermarket_mission = addMission("go to carrefour", "it's a great supermarket", ["courses"])
        self.jobsMission = addMission("apply to jobs", "because I'm unemployed", ["carriere"])
        addMission("study for test", "", ["devoirs"])
        addMission("write cv", "", ["devoirs", "francais"])
        addMission("language exchage", "", ["francais", "social"])

        positionner_pour_mission(self.jobsMission.id, self.josie.id, "just because")
        time.sleep(2)
        affectuer_mission(self.jobsMission.id, self.josie.id)


    def test_all(self):

        def test_login():
            self.assertEqual(self.josie, login("josieposie", "password1"))
            self.assertEqual(self.felipe, login("felipemaple", "password2"))
            self.assertEqual(self.pablo, login("pabloingles", "password3"))
            self.assertEqual(self.admin, login("adminaccount", "password4"))


        def test_response_obj_1_mission():

            mission = get_mission_by_id(self.jobsMission.id)
            self.assertEqual(mission.title, "apply to jobs")
            self.assertEqual(mission.description, "because I'm unemployed")
            self.assertListEqual(mission.categories, ["carriere"])
            self.assertEqual(mission.status, Status.AFFECTE.value)
            self.assertEqual(mission.ingenieur_affecte.id, self.josie.id)
            self.assertEqual(mission.ingenieurs_positionnees[0].id, self.josie.id)

        def test_ingenieur_evolution_response_obj():
            evolution = getEvolutionPourIngenieur(self.josie.id)
            self.assertTrue(evolution[0].description.startswith("Josie a positionné pour mission apply to jobs avec les souhaits just because à "))
            self.assertTrue(evolution[1].description.startswith("Josie a été affectué la mission apply to jobs à "))

        def test_get_missions_a_affecter():
            missions = getMissionsAAffecter()
            self.assertEqual(len(missions), 4)

        def test_get_missions_a_affecter_categories():
            missions_devoirs = getMissionsAAffecter(categories=["devoirs"])
            self.assertEqual(len(missions_devoirs), 2)
            missions_francais = getMissionsAAffecter(categories=["francais"])
            self.assertEqual(len(missions_francais), 2)
            missions_devoirs_francais = getMissionsAAffecter(categories=["devoirs", "francais"])
            self.assertEqual(len(missions_devoirs_francais), 3)

        def test_positionner_flow():
            positionner_pour_mission(self.supermarket_mission.id, self.felipe.id, "i want to compare all of the products")
            positionner_pour_mission(self.supermarket_mission.id, self.pablo.id, "i want felipe to hurry up")

            def test_positionner():
                self.assertEqual(len(list(Positionnement.query.filter_by(mission_id=self.supermarket_mission.id))), 2)

            def test_get_voeux_pour_mission():
                supermarket_voeux = getVoeuxPourMission(self.supermarket_mission.id)
                self.assertListEqual(sorted(supermarket_voeux),  sorted(list({"i want to compare all of the products", "i want felipe to hurry up"})))

            def test_affectuer_flow():
                affectuer_mission(self.supermarket_mission.id, self.pablo.id)

                def test_affectuer():
                    self.assertEqual(len(list(Affectuation.query.filter_by(mission_id=self.supermarket_mission.id))), 1)
                    self.assertEqual(len(getMissionsAffectes()), 2)

                def test_clore_flow():
                    cloreMission(self.supermarket_mission.id)
                    self.supermarket_mission = get_mission_by_id(self.supermarket_mission.id)

                    def test_clore_mission():
                        self.assertEqual(self.supermarket_mission.status, Status.CLOS.value)
                        self.assertEqual(len(getMissionsAAffecter()), 3)

                    def test_supprimer_mission():
                        supprimerMission(self.supermarket_mission.id)
                        self.assertEqual(len(list(Affectuation.query.filter_by(mission_id=self.supermarket_mission.id))), 0)
                        self.assertEqual(len(list(Positionnement.query.filter_by(mission_id=self.supermarket_mission.id))), 0)
                        self.assertEqual(len(Category.query.filter_by(name="courses").first().missions), 0)
                        self.assertEqual(len(list(Action.query.filter_by(mission_id=self.supermarket_mission.id))), 0)
                        self.pablo = get_ingenieur_by_id(self.pablo.id)
                        self.assertEqual(len(self.pablo.missions_positionnes), 0)
                        self.assertEqual(len(self.pablo.missions_affectues), 0)

                    test_clore_mission()
                    test_supprimer_mission()

                test_affectuer()
                test_clore_flow()

            test_positionner()
            test_get_voeux_pour_mission()
            test_affectuer_flow()

        test_login()
        test_get_missions_a_affecter()
        test_get_missions_a_affecter_categories()
        test_positionner_flow()
        test_response_obj_1_mission()
        test_ingenieur_evolution_response_obj()


    def tearDown(self):
        db.drop_all()


def main():
    ut = UnitTests()
    ut.setUp()
    ut.test_all()
    ut.tearDown()

if __name__ == "__main__":
    main()