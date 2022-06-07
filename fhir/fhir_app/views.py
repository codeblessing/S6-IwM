from django.views import View
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
import requests
import json
import plotly.express as px
from datetime import date

observation_get = "http://localhost:8080/baseR4/Observation?_count="
medication_get = "http://localhost:8080/baseR4/MedicationRequest?_count="
observation_versions_get = "http://localhost:8080/baseR4/Observation/"


class ChartView(View):
    def get(self, request, id, property_code):
        count = "50"
        min_date = request.GET.get("date_min")
        max_date = request.GET.get("date_max")

        if min_date == None:
            min_date = ""
        if max_date == None:
            max_date = ""
        suffix = "&patient=" + id + "&date=gt" + min_date + "&date=lt" + max_date
        total = requests.get(observation_get + suffix).text
        json_total = json.loads(total)
        number_of_records = json_total["total"]
        if int(count) > number_of_records:
            raw_data = requests.get(observation_get + count + suffix).text
            plot_data = json.loads(raw_data)
        else:
            raw_data = requests.get(observation_get + count + suffix).text
            plot_data = json.loads(raw_data)
            next_page = plot_data["link"][1]["url"]
            for _ in range(0, number_of_records - len(plot_data["entry"]), int(count)):
                raw_data_2 = requests.get(next_page).text
                json_data_2 = json.loads(raw_data_2)
                if json_data_2["link"][1]["relation"] == "next":
                    next_page = json_data_2["link"][1]["url"]

                plot_data["entry"].extend(json_data_2["entry"][::])

            dates = []
            data = []

            for d in plot_data["entry"]:

                if d["resource"]["code"]["coding"][0]["code"] == property_code:
                    if d["resource"].get("valueQuantity") is not None:
                        label = (
                            d["resource"]["code"]["text"]
                            + " ["
                            + d["resource"]["valueQuantity"]["unit"]
                            + "]"
                        )
                    else:
                        label = (
                            d["resource"]["code"]["text"]
                            + " ["
                            + d["resource"]["component"][0]["valueQuantity"]["unit"]
                            + "]"
                        )
                    dt = date(
                        year=int(d["resource"]["effectiveDateTime"][:4]),
                        month=int(d["resource"]["effectiveDateTime"][5:7]),
                        day=int(d["resource"]["effectiveDateTime"][8:10]),
                    )
                    dates.append(dt)
                    if d["resource"].get("valueQuantity") is not None:
                        data.append(d["resource"]["valueQuantity"]["value"])
                    else:
                        data.append(
                            d["resource"]["component"][0]["valueQuantity"]["value"]
                        )

            figure = px.line(
                x=dates, y=data, labels={"x": "Date", "y": label}, markers=True
            )
            chart = figure.to_html()
            context = {"chart": chart, "patient": plot_data}

        if number_of_records == 0:
            context = {"chart": "No data available for given period!"}

        return render(request, "chart.html", context=context)


class PatientListView(View):
    def get(self, request):
        count = "50"

        name_contains = request.GET.get("name_contains")
        if name_contains != "" and name_contains is not None:
            count = "50"
            raw_data = requests.get(
                "http://localhost:8080/baseR4/Patient?_count="
                + count
                + "&family="
                + name_contains
            ).text
            json_data = json.loads(raw_data)

            return render(request, "list_template.html", context=json_data)
        else:
            total = requests.get("http://localhost:8080/baseR4/Patient?_count=0").text
            json_total = json.loads(total)
            raw_data = requests.get(
                "http://localhost:8080/baseR4/Patient?_count=" + count
            ).text
            json_data = json.loads(raw_data)
            next_page = json_data["link"][1]["url"]
            for _ in range(
                0, json_total["total"] - len(json_data["entry"]), int(count)
            ):
                print(next_page)
                raw_data_2 = requests.get(next_page).text
                json_data_2 = json.loads(raw_data_2)
                if json_data_2["link"][1]["relation"] == "next":
                    next_page = json_data_2["link"][1]["url"]
                json_data["entry"].extend(json_data_2["entry"][::])

            return render(request, "list_template.html", context=json_data)


class PatientView(View):
    def get(self, request, id):
        json_data_medication = {}
        json_data_observation = {}
        json_data = {}

        min_date = request.GET.get("date_min")
        max_date = request.GET.get("date_max")

        if min_date == None:
            min_date = ""
        if max_date == None:
            max_date = ""
        suffix = "&patient=" + id + "&date=gt" + min_date + "&date=lt" + max_date
        # patient data
        raw_data_patient = requests.get(
            "http://localhost:8080/baseR4/Patient?&_id=" + id
        ).text
        json_data = json.loads(raw_data_patient)

        # patient observation
        count = "50"
        total = requests.get(observation_get + suffix).text
        json_total = json.loads(total)
        number_of_records = json_total["total"]
        if int(count) > number_of_records:
            raw_data = requests.get(observation_get + count + suffix).text
            json_data_observation = json.loads(raw_data)
        else:
            raw_data = requests.get(observation_get + count + suffix).text
            json_data_observation = json.loads(raw_data)
            next_page = json_data_observation["link"][1]["url"]
            for _ in range(
                0, number_of_records - len(json_data_observation["entry"]), int(count)
            ):
                raw_data_2 = requests.get(next_page).text
                json_data_2 = json.loads(raw_data_2)
                if json_data_2["link"][1]["relation"] == "next":
                    next_page = json_data_2["link"][1]["url"]

                json_data_observation["entry"].extend(json_data_2["entry"][::])

        # for entry in json_data_observation["entry"]:
        #     version_raw_data = requests.get(
        #         observation_versions_get + entry["resource"]["id"] + "/_history"
        #     ).text
        #     version_json_data = json.loads(version_raw_data)
        #     entry["versions"] = version_json_data

        # patient medication
        count = "50"
        total = requests.get(medication_get + suffix).text
        json_total = json.loads(total)
        number_of_records = json_total["total"]
        if int(count) > number_of_records:
            count = number_of_records
            raw_data = requests.get(medication_get + str(count) + suffix).text
            json_data_medication = json.loads(raw_data)
            data = {
                "patient_list": json_data,
                "observations": json_data_observation,
                "medication": json_data_medication,
            }
            return render(request, "patient_template.html", context=data)

        raw_data = requests.get(medication_get + str(count) + suffix).text
        json_data_medication = json.loads(raw_data)
        next_page = json_data_medication["link"][1]["url"]
        for _ in range(0, number_of_records, int(count)):
            raw_data_2 = requests.get(next_page).text
            json_data_2 = json.loads(raw_data_2)
            if json_data_2["link"][1]["relation"] == "next":
                next_page = json_data_2["link"][1]["url"]

            json_data_medication["entry"].extend(json_data_2["entry"][::])

        data = {
            "patient_list": json_data,
            "observations": json_data_observation,
            "medication": json_data_medication,
        }
        return render(request, "patient_template.html", context=data)
