from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, RelationshipTo, RelationshipFrom


class Game(StructuredNode):
    name = StringProperty(required=True)

    steam_app_id = IntegerProperty(unique_index=True)

    # utility property, to determine games that are not in a good state, i.e. have test identiers for their name and such
    incomplete = BooleanProperty()

    achievements = RelationshipTo("Achievement", "hasAchievement")
    owned_by = RelationshipFrom("Player", "ownedBy")


class Achievement(StructuredNode):
    #    id = StringProperty(unique_index=True, required=True)
    api_name = StringProperty(required=True, db_property="api_name")

    description = StringProperty()
    image_url = StringProperty(db_property="imageUrl")
    source = StringProperty()

    achieved_in = RelationshipFrom("Game", "achievedIn")
    unlocked_by = RelationshipFrom("Player", "unlockedBy")


class Player(StructuredNode):
    name = StringProperty(required=True)
    steam_id = StringProperty(db_property="steamId")
    xbox_account = StringProperty(db_property="xboxAccount")

    games = RelationshipTo("Game", "owns")
    unlocked_achievements = RelationshipTo("Achievement", "hasUnlocked")
