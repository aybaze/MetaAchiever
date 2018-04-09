from pymodm import fields, MongoModel


class Achievement(MongoModel):

    id = fields.CharField(primary_key=True)
    name = fields.CharField()
    description = fields.CharField()
    image_url = fields.URLField(blank=True)
    source = fields.CharField()

    def serialize(self):
        return self.to_son()
