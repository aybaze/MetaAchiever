from py2neo.ogm import Property, GraphObject, RelatedTo, RelatedFrom


class BaseObject(GraphObject):
    def to_dict(self):
        return self.__ogm__.node


class Game(BaseObject):
    __primarykey__ = "id"

    id = Property()
    name = Property()

    achievements = RelatedTo("Achievement", "hasAchievement")
    owned_by = RelatedFrom("Player", "ownedBy")


class Achievement(BaseObject):
    __primarykey__ = "id"

    id = Property()
    name = Property()
    description = Property()
    image_url = Property(key="imageUrl")
    source = Property()

    achieved_in = RelatedFrom("Game", "achievedIn")


class Player(BaseObject):
    # TODO: use a global unique identifier
    __primarykey__ = "name"

    name = Property()

    games = RelatedTo("Game", "owns")
