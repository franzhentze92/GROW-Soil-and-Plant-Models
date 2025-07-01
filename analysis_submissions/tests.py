from django.test import TestCase

# Create your tests here.
from .models import ReportSubmission

# false > False
# null > None
# python manage.py test analysis_submissions

class ReportSubmissionTest(TestCase):
    def setUp(self):
        self.mock_report = {
            "title": "Soil Therapy Report",
            "user": {
                "date": "2025-05-13",
                "name": "M & BJ McInerney ",
                "address": "",
                "land": "",
                "sample_rec": "",
                "email": "",
                "sample_red": ""
            },
            "include_nutrients_explanation": False,
            "soilCrop": "soil crop text",
            "soilLabType": "soil lab test",
            "sample_paddock_farm_assignments": [
                {
                    "sample": "Creek South ",
                    "farm": None,
                    "paddock": None
                }
            ],
            "paddocks": {
                "Creek South ": {
                    "table": "\n<table class=\"table table-bordered mb-0\" id=\"table-component\"> ..Very long HTML </table>\n                ",
                    "nutrient_ratios_table": "",
                    "dataset_processed": {
                        "albrecht": {
                            "has_comparison": [
                                [
                                    "Nitrate-N",
                                    "NO3-N",
                                    "2.1",
                                    "10",
                                    "20",
                                    "6.7",
                                    "30",
                                    ""
                                ],
                                [
                                    "Ammonium-N",
                                    "NH4-N",
                                    "1.3",
                                    "10",
                                    "20",
                                    "6.7",
                                    "30",
                                    ""
                                ]
                            ],
                            "base_saturation": [
                                [
                                    "Calcium",
                                    None,
                                    "53.05",
                                    None,
                                    "62.00",
                                    "0.00",
                                    "93.10",
                                    ""
                                ],
                                [
                                    "Magnesium",
                                    None,
                                    "12.25",
                                    None,
                                    "18.00",
                                    "0.00",
                                    "27.00",
                                    ""
                                ]
                            ]
                        },
                        "lamotte": [
                            [
                                "Calcium",
                                "",
                                487,
                                1000,
                                2000,
                                "",
                                "",
                                ""
                            ],
                            [
                                "Magnesium",
                                "",
                                71.6,
                                140,
                                285,
                                "",
                                "",
                                ""
                            ]
                        ],
                        "tec": 4.65,
                        "cec": 3.69,
                        "caMgRatio": {
                            "name": "Ca/Mg Ratio",
                            "value": 4.33,
                            "ideal": 3.4,
                            "lower": 0,
                            "deficient": 0,
                            "excessive": 6.5
                        },
                        "tae_data_selected": [
                            {
                                "identification": "Na",
                                "name": "Sodium",
                                "value": 50,
                                "display_value": "<50.0",
                                "icon": "<",
                                "lower": 100,
                                "upper": 500
                            },
                            {
                                "identification": "K",
                                "name": "Potassium",
                                "value": 1510,
                                "display_value": "1510.0",
                                "icon": "",
                                "lower": 200,
                                "upper": 2000
                            }
                        ]
                    },
                    "recommendations": {
                        "explanation": {
                            "Organic Matter": "The Soil Organic Matter (SOM) in ..",
                            "CEC": "The Cation Exchange Capacity (CEC) in your soil is low, indicating that the soil has a limited ability to retain nutrients and moisture. This is often characteristic of sandy soils, where nutrients quickly leach away, reducing their availability to plants. Low CEC soils require frequent fertilization and organic matter additions to maintain adequate nutrient levels. To improve CEC, consider incorporating compost, biochar, humic substances, and clay minerals to enhance the soil’s nutrient-holding capacity.",
                            "Soil pH": "The soil pH is driven by the ..",
                            "Base Saturation": "The base saturation refers to ..",
                            "Available Nutrients": "This section presents the levels of key plant-available nutrients found in the soil at the time of sampling.. ",
                            "Lamotte Reams": "This test measures the ..",
                            "TAE": "This section shows the Total Acid Extractable (TAE) nutrient levels ..."
                        },
                        "form_data": {
                            "crop_group": "191",
                            "nutrient_deficient": [
                                {
                                    "category": "CEC",
                                    "value": "CEC"
                                },
                                {
                                    "category": "Soil pH",
                                    "value": "pH-level"
                                },
                                {
                                    "category": "Organic Matter",
                                    "value": "Organic Matter"
                                },
                                {
                                    "category": "Available Nutrients",
                                    "value": "Organic Carbon"
                                },
                                {
                                    "category": "TAE",
                                    "value": "Sulfur"
                                }
                            ],
                            "nutrient_excess": [
                                {
                                    "category": "Available Nutrients",
                                    "value": "Aluminium"
                                },
                                {
                                    "category": "Base Saturation",
                                    "value": "Aluminum"
                                }
                            ],
                            "nutrient_optimal": [
                                {
                                    "category": "Available Nutrients",
                                    "value": "Paramagnetism"
                                },
                                {
                                    "category": "Available Nutrients",
                                    "value": "Ca/Mg Ratio"
                                }
                            ]
                        }
                    }
                }
            }
        }

    def test_create_and_retrieve_report_submission(self):
        submission = ReportSubmission.objects.create(
            user_id=123,
            user_email="test@example.com",
            user_role="user",
            analysis_type="soil",
            report_data=self.mock_report
        )

        self.assertIsNotNone(submission.report_id)
        self.assertEqual(submission.user_email, "test@example.com")
        self.assertEqual(submission.report_data["title"], "Soil Therapy Report")

        # Retrieve it
        fetched = ReportSubmission.objects.get(report_id=submission.report_id)
        self.assertEqual(fetched.report_data["paddocks"]["Creek South "]["dataset_processed"]["cec"], 3.69)

        fetched = ReportSubmission.objects.get(user_email="test@example.com", user_role="user")
        self.assertEqual(fetched.report_data["user"]["name"], "M & BJ McInerney ")