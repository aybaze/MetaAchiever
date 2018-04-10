from py2neo.ogm import Property, GraphObject, RelatedTo, RelatedFrom


class Game(GraphObject):
    __primarykey__ = "name"

    name = Property()
    achievements = RelatedFrom("Achievement", "ACHIEVED_IN")


class Achievement(GraphObject):
    __primarykey__ = "id"

    id = Property()
    name = Property()
    description = Property()
    image_url = Property(key="imageUrl")
    source = Property()

    achieved_in = RelatedTo(Game)

    def serialize(self):
        return self.__ogm__.node
