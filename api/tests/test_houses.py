import pytest

HOUSE = {"bedrooms": 3, "bathrooms": 2.5, "sqft_living": 1800, "grade": 8, "zipcode": "98103"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_index_serves_the_houses_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>King County Houses</title>" in response.text


def test_create_and_read_a_house(client):
    created = client.post("/houses", json=HOUSE)
    assert created.status_code == 201
    house = created.json()
    assert house == {**HOUSE, "id": house["id"]}
    assert client.get(f"/houses/{house['id']}").json() == house


def test_list_houses_in_id_order_and_filter_by_zipcode(client):
    client.post("/houses", json=HOUSE)
    client.post("/houses", json={**HOUSE, "zipcode": "98004"})
    assert [h["zipcode"] for h in client.get("/houses").json()] == ["98103", "98004"]
    assert [h["zipcode"] for h in client.get("/houses?zipcode=98004").json()] == ["98004"]


def test_update_replaces_every_field(client):
    house_id = client.post("/houses", json=HOUSE).json()["id"]
    changed = {"bedrooms": 4, "bathrooms": 3.0, "sqft_living": 2400, "grade": 9, "zipcode": "98004"}
    response = client.put(f"/houses/{house_id}", json=changed)
    assert response.status_code == 200
    assert response.json() == {**changed, "id": house_id}


def test_delete_then_404(client):
    house_id = client.post("/houses", json=HOUSE).json()["id"]
    assert client.delete(f"/houses/{house_id}").status_code == 204
    assert client.get(f"/houses/{house_id}").status_code == 404
    assert client.delete(f"/houses/{house_id}").status_code == 404


def test_missing_house_returns_404_for_update(client):
    assert client.put("/houses/999", json=HOUSE).status_code == 404


@pytest.mark.parametrize(
    "field, value",
    [
        ("bedrooms", -1),
        ("bathrooms", 2.3),
        ("sqft_living", 0),
        ("grade", 14),
        ("zipcode", "981"),
        ("zipcode", "abcde"),
    ],
)
def test_invalid_values_are_rejected(client, field, value):
    assert client.post("/houses", json={**HOUSE, field: value}).status_code == 422


def test_missing_field_is_rejected(client):
    incomplete = {k: v for k, v in HOUSE.items() if k != "grade"}
    assert client.post("/houses", json=incomplete).status_code == 422
