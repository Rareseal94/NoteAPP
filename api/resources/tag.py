from api import auth, abort, g, Resource, reqparse
from api.models.tag import TagModel
from api.schemas.tag import TagSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Tags'])
class TagsResource(MethodResource):
    @marshal_with(TagSchema)
    @doc(summary="Get tag by id")
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"User with id={tag_id} not found")
        return tag, 200

    @auth.login_required(role="admin")
    @doc(description='Edit tag')
    @marshal_with(TagSchema)
    @use_kwargs({"Tag": fields.Str()})
    @doc(security=[{"basicAuth": []}])
    def put(self, tag_id, **kwargs):
        tag = TagModel.query.get(tag_id)
        tag.name = kwargs["tag"]
        tag.save()
        return tag, 200

    @auth.login_required(role="admin")
    @doc(description='Delete tag by id')
    @marshal_with(TagSchema)
    @doc(security=[{"basicAuth": []}])
    @doc(responses={401: {"description": "Not auth"}})
    @doc(responses={404: {"description": "Not found"}})
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id:{tag_id} not found")
        tag.delete()
        return tag, 200


@doc(tags=['Tags'])
class TagsListResource(MethodResource):
    @doc(summary="Get all tags")
    @marshal_with(TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()
        return tags, 200

    @doc(summary="Create new tag")
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema)
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        return tag, 201
