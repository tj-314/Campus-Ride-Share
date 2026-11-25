import pytest
from models import RidePost, ValidationError
from service import PostService

@pytest.fixture
def valid():
    return dict(post_type="offer", destination="St. Louis", travel_date="2099-12-01", departure_time="15:00", seats="2", contact="demo@example.invalid")

@pytest.fixture
def service(tmp_path):
    return PostService(tmp_path / "test.db")

@pytest.mark.parametrize("seats,accepted", [("0",False),("1",True),("2",True),("-1",False),("1.5",False),("",False)])
def test_TC02_TC03_seat_boundary(valid,seats,accepted):
    # Arrange
    valid["seats"] = seats
    # Act / Assert
    if accepted:
        assert RidePost.validate(valid)["seats"] == int(seats)
    else:
        with pytest.raises(ValidationError):
            RidePost.validate(valid)

def test_TC01_create_owned_offer(service,valid):
    # Arrange
    actor = "alex"
    # Act
    post_id = service.create(actor,valid)
    # Assert
    assert service.get(actor,post_id)["owner"] == actor

def test_TC04_missing_destination_not_saved(service,valid):
    # Arrange
    valid["destination"] = ""
    # Act / Assert
    with pytest.raises(ValidationError) as exc:
        service.create("alex",valid)
    assert "destination" in exc.value.errors
    assert service.browse("alex") == []

def test_TC05_request_needs_no_seats(service,valid):
    # Arrange
    valid.update(post_type="request",seats="")
    # Act
    post_id=service.create("alex",valid)
    # Assert
    assert service.get("alex",post_id)["seats"] is None

def test_TC06_combined_filter(service,valid):
    # Arrange
    service.create("alex",valid)
    service.create("alex",dict(valid,destination="Memphis"))
    # Act
    rows=service.browse("alex","st. louis","2099-12-01")
    # Assert
    assert len(rows)==1

def test_TC07_other_owner_cannot_edit(service,valid):
    # Arrange
    post_id=service.create("alex",valid)
    # Act / Assert
    with pytest.raises(PermissionError):
        service.update("jordan",post_id,dict(valid,destination="Changed"))
    assert service.get("alex",post_id)["destination"]=="St. Louis"

def test_TC08_delete_requires_confirmation(service,valid):
    # Arrange
    post_id=service.create("alex",valid)
    # Act
    removed=service.delete("alex",post_id,False)
    # Assert
    assert removed is False
    assert service.get("alex",post_id)

def test_TC09_confirmed_delete(service,valid):
    # Arrange
    post_id=service.create("alex",valid)
    # Act
    removed=service.delete("alex",post_id,True)
    # Assert
    assert removed is True
    with pytest.raises(LookupError):
        service.get("alex",post_id)

@pytest.mark.parametrize("actor,owner,allowed",[(None,"alex",False),("jordan","alex",False),("alex","alex",True)])
def test_owner_authorization_branches(actor,owner,allowed):
    # Arrange: inputs supplied by table
    # Act / Assert
    if allowed:
        assert PostService.authorize_owner(actor,owner) is True
    else:
        with pytest.raises(PermissionError):
            PostService.authorize_owner(actor,owner)

def test_unauthenticated_creation_denied(service,valid):
    # Arrange: no authenticated actor
    # Act / Assert
    with pytest.raises(PermissionError):
        service.create(None,valid)

def test_owner_can_update(service,valid):
    # Arrange
    post_id=service.create("alex",valid)
    # Act
    service.update("alex",post_id,dict(valid,destination="Memphis"))
    # Assert
    assert service.get("alex",post_id)["destination"]=="Memphis"
