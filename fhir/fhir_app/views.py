from django.views import View
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
import requests
import json


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
            for i in range(0, json_total["total"] - 1, int(count)):
                if i == 0:
                    raw_data = requests.get(
                        "http://localhost:8080/baseR4/Patient?_count=" + count
                    ).text
                    json_data = json.loads(raw_data)
                    next_page = json_data["link"][1]["url"]
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
        count = "50"

        min_date = request.GET.get("date_min")
        max_date = request.GET.get("date_max")

        if min_date == None:
            min_date = ""
        if max_date == None:
            max_date = ""
        suffix = id + "&date=gt" + min_date + "&date=lt" + max_date
        # patient data
        raw_data_patient = requests.get(
            "http://localhost:8080/baseR4/Patient?&_id=" + id
        ).text
        json_data = json.loads(raw_data_patient)

        # patient observation
        count="50"
        total = requests.get(
            "http://localhost:8080/baseR4/Observation?_count=0&patient=" + suffix
        ).text
        json_total = json.loads(total)
        number_of_records = json_total["total"]
        if int(count) > number_of_records:
            raw_data = requests.get(
                    "http://localhost:8080/baseR4/Observation?_count="
                    + count
                    + "&patient="
                    + suffix
            ).text
            json_data_observation = json.loads(raw_data)
        else:
            for i in range(0, number_of_records, int(count)):
                print(i)
                if i == 0:
                    raw_data = requests.get(
                        "http://localhost:8080/baseR4/Observation?_count="
                        + count
                        + "&patient="
                        + suffix
                    ).text
                    json_data_observation = json.loads(raw_data)
                    next_page = json_data_observation["link"][1]["url"]
                    
                
                raw_data_2 = requests.get(next_page).text
                json_data_2 = json.loads(raw_data_2)
                if json_data_2["link"][1]["relation"] == "next":
                    next_page = json_data_2["link"][1]["url"]

                json_data_observation["entry"].extend(json_data_2["entry"][::])
            

        # patient medication
        count = "50"
        total = requests.get(
            "http://localhost:8080/baseR4/MedicationRequest?_count=0&patient=" + suffix
        ).text
        json_total = json.loads(total)
        number_of_records = json_total["total"]
        if int(count) > number_of_records:
            count = number_of_records
            raw_data = requests.get(
                    "http://localhost:8080/baseR4/MedicationRequest?_count="
                    + str(count)
                    + "&patient="
                    + suffix
                ).text
            json_data_medication = json.loads(raw_data)
            data = {
            "patient_list": json_data,
            "observations": json_data_observation,
            "medication": json_data_medication,
            }
            return render(request, "patient_template.html", context=data)

        for i in range(0, number_of_records, int(count)):
            if i == 0:
                raw_data = requests.get(
                    "http://localhost:8080/baseR4/MedicationRequest?_count="
                    + str(count)
                    + "&patient="
                    + suffix
                ).text
                json_data_medication = json.loads(raw_data)
                next_page = json_data_medication["link"][1]["url"]

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
