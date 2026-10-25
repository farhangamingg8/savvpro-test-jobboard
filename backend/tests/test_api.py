def create_job(client, data):
    response = client.post("/api/jobs", json=data)
    assert response.status_code == 201, response.text
    return response.json()


def apply(client, job_id, data):
    response = client.post(f"/api/jobs/{job_id}/applications", json=data)
    assert response.status_code == 201, response.text
    return response.json()


def test_job_creation_and_structured_salary_validation(client, job_data):
    job = create_job(client, job_data)
    assert job["title"] == job_data["title"]
    assert job["accepting_applications"] is True

    invalid = {**job_data, "salary_min": 150000, "salary_max": 100000}
    response = client.post("/api/jobs", json=invalid)
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "salary_min" in body["error"]["details"][0]["message"]


def test_pagination_has_metadata_and_stable_pages(client, job_data):
    for index in range(5):
        create_job(client, {**job_data, "title": f"Role {index}"})

    first = client.get("/api/jobs?page=1&per_page=2").json()
    second = client.get("/api/jobs?page=2&per_page=2").json()
    assert first["total_count"] == 5
    assert first["page"] == 1
    assert first["per_page"] == 2
    assert len(first["results"]) == 2
    assert len(second["results"]) == 2
    assert {item["id"] for item in first["results"]}.isdisjoint(
        {item["id"] for item in second["results"]}
    )


def test_simultaneous_filters_and_include_closed(client, job_data):
    matching = create_job(client, job_data)
    create_job(
        client,
        {
            **job_data,
            "title": "Designer",
            "department": "Design",
            "location": "hybrid",
            "required_skills": ["Figma"],
        },
    )
    response = client.get("/api/jobs?department=Engineering&location=remote&skill=python")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["results"]] == [matching["id"]]

    partial_department = client.get("/api/jobs?department=engine&location=remote")
    assert [item["id"] for item in partial_department.json()["results"]] == [matching["id"]]

    title_search = client.get("/api/jobs?search=platform")
    assert [item["id"] for item in title_search.json()["results"]] == [matching["id"]]

    assert client.post(f"/api/jobs/{matching['id']}/close").status_code == 200
    assert client.get("/api/jobs").json()["total_count"] == 1
    assert client.get("/api/jobs?include_closed=true").json()["total_count"] == 2


def test_duplicate_and_applicant_cap_rules(client, job_data, application_data):
    job = create_job(client, {**job_data, "max_applicants": 1})
    apply(client, job["id"], application_data)

    duplicate = client.post(f"/api/jobs/{job['id']}/applications", json=application_data)
    # Capacity is checked first and still returns a clear business conflict.
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "applicant_cap_reached"
    detail = client.get(f"/api/jobs/{job['id']}").json()
    assert detail["is_closed"] is False
    assert detail["accepting_applications"] is False

    second_job = create_job(client, job_data)
    apply(client, second_job["id"], application_data)
    duplicate = client.post(f"/api/jobs/{second_job['id']}/applications", json=application_data)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "duplicate_application"


def test_status_workflow_preserves_history_and_blocks_backward_move(client, job_data, application_data):
    job = create_job(client, job_data)
    application = apply(client, job["id"], application_data)
    assert application["status"] == "pending"
    assert len(application["history"]) == 1

    shortlisted = client.patch(
        f"/api/applications/{application['id']}/status",
        json={"status": "shortlisted", "note": "Strong relevant experience"},
    )
    assert shortlisted.status_code == 200
    offered = client.patch(
        f"/api/applications/{application['id']}/status",
        json={"status": "offered", "note": "Interview panel approved"},
    )
    assert offered.status_code == 200
    assert [event["to_status"] for event in offered.json()["history"]] == [
        "pending",
        "shortlisted",
        "offered",
    ]

    backwards = client.patch(
        f"/api/applications/{application['id']}/status",
        json={"status": "pending", "note": "Try to undo"},
    )
    assert backwards.status_code == 409
    assert backwards.json()["error"]["code"] == "invalid_status_transition"
    filtered = client.get(f"/api/jobs/{job['id']}/applications?status=offered")
    assert len(filtered.json()) == 1


def test_close_preserves_pending_but_blocks_new_applications(client, job_data, application_data):
    job = create_job(client, job_data)
    pending = apply(client, job["id"], application_data)
    assert client.post(f"/api/jobs/{job['id']}/close").status_code == 200

    applications = client.get(f"/api/jobs/{job['id']}/applications").json()
    assert applications[0]["id"] == pending["id"]
    assert applications[0]["status"] == "pending"
    new_application = {**application_data, "email": "grace@example.com"}
    blocked = client.post(f"/api/jobs/{job['id']}/applications", json=new_application)
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "job_closed"


def test_stats_are_computed_from_database(client, job_data, application_data):
    first = create_job(client, job_data)
    second = create_job(client, {**job_data, "title": "Recruiter", "department": "People"})
    apply(client, first["id"], application_data)
    apply(client, second["id"], {**application_data, "email": "new@example.com"})
    client.post(f"/api/jobs/{second['id']}/close")

    stats = client.get("/api/stats")
    assert stats.status_code == 200
    assert stats.json() == {
        "total_jobs": 2,
        "open_jobs": 1,
        "closed_jobs": 1,
        "total_applications": 2,
        "avg_applications_per_job": 1.0,
        "top_department": "Engineering",
    }

