from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.models.user import UserModel
from api.models.tag import TagModel
from api.schemas.note import NoteSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields
import pdb


@doc(tags=['Notes'])
class NoteResource(MethodResource):
    @auth.login_required
    @marshal_with(NoteSchema)
    @doc(summary="Get note by id", security=[{"basicAuth": []}])
    def get(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        return note, 200

    @auth.login_required
    @marshal_with(NoteSchema)
    def put(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.text = note_data["text"]

        note.private = note_data.get("private") or note.private
        # if note_data["private"]:
        #     note.private = note_data["private"]

        note.save()
        return note, 200

    @auth.login_required
    @doc(description='Delete note by id')
    @marshal_with(NoteSchema)
    @doc(security=[{"basicAuth": []}])
    @doc(responses={401: {"description": "Not auth"}})
    @doc(responses={404: {"description": "Not found"}})
    def delete(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        note.delete()
        return note, 200


@doc(tags=['Notes'])
class NotesListResource(MethodResource):
    @auth.login_required
    @marshal_with(NoteSchema(many=True))
    @doc(summary="Get user by id", security=[{"basicAuth": []}])
    def get(self):
        author = g.user
        notes = NoteModel.query.filter_by(author_id=author.id)
        return notes, 200

    @auth.login_required
    @doc(summary="Get note", security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True))
    @use_kwargs(NoteSchema, code=201)
    def post(self, **kwargs):
        author = g.user
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201


@doc(tags=['Notes'])
class NoteAddTagsResource(MethodResource):
    @use_kwargs({"tags": fields.List(fields.Int())})
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id, **kwargs):
        note = NoteModel.query.get(note_id)
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.append(tag)
        note.save()
        return note, 200


@doc(tags=['NoteFilter'])
class NoteFilterResource(MethodResource):
    @use_kwargs({"tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, **kwargs):
        notes = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
        return notes, 200

