# pyrefly: ignore-errors

import json

from punyecs import Trait, World, give_traits, requirements


@give_traits(Trait(x=0.0, y=0.0))
class SerializableEntity:
    pass


def test_deserialize_loads_entities_from_json(tmp_path):
    w = World()

    @requirements(w, Trait(x=0.0, y=0.0))
    def move(e, dt):
        e.x += 0.1

    data = {
        "entities": [
            {"x": 0.0, "y": 0.0, "obj_name": "orc_1", "cls_name": "SerializableEntity"}
        ]
    }
    src = tmp_path / "world.json"
    src.write_text(json.dumps(data))

    w.deserialize(str(src))

    assert len(w.entities) == 1
    assert w.entities[0] is SerializableEntity
    assert w.entities[0].__name__ == "orc_1"
    assert len(w.groups) == 1
    assert w.groups[0].entities == [SerializableEntity]

    SerializableEntity.__name__ = "SerializableEntity"


def test_serialize_round_trip(tmp_path):
    w = World()
    entity = SerializableEntity()
    w.add(entity)

    dest = tmp_path / "world.json"
    w.serialize(str(dest))

    assert json.loads(dest.read_text()) == {
        "entities": [
            {
                "x": 0.0,
                "y": 0.0,
                "obj_name": "SerializableEntity",
                "cls_name": "SerializableEntity",
            }
        ]
    }