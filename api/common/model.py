from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, RelationshipTo, RelationshipFrom


def to_dict(node: StructuredNode):
    d = {}

    for key, prop in node.__all_properties__:
        db_property = prop.db_property or key

        if key in node.__properties__:
            d[db_property] = node.__properties__[key]
        elif prop.has_default:
            d[db_property] = prop.default_value()
        else:
            d[db_property] = None

    return d


class Game(StructuredNode):
    name = StringProperty(required=True)

    steam_app_id = IntegerProperty(unique_index=True, db_property="steamAppID")

    # utility property, to determine games that are not in a good state, i.e. have test identiers for their name and such
    incomplete = BooleanProperty()

    achievements = RelationshipTo("Achievement", "HAS_ACHIEVEMENT")
    owned_by = RelationshipFrom("Player", "OWNS")


class Achievement(StructuredNode):
    #    id = StringProperty(unique_index=True, required=True)
    api_name = StringProperty(required=True, db_property="apiName")

    description = StringProperty()
    image_url = StringProperty(db_property="imageUrl")
    source = StringProperty()

    achieved_in = RelationshipFrom("Game", "HAS_ACHIEVEMENT")
    unlocked_by = RelationshipFrom("Player", "HAS_UNLOCKED")


class Player(StructuredNode):
    name = StringProperty(required=True)
    steam_id = StringProperty(db_property="steamId")
    xbox_account = StringProperty(db_property="xboxAccount")

    games = RelationshipTo("Game", "OWNS")
    unlocked_achievements = RelationshipTo("Achievement", "HAS_UNLOCKED")
