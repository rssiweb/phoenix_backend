from flask import request, Blueprint
from app import db, jsonify
from app.models import DistributionType
from app.utils import decorators
from app.utils.constants import StatusErrors as errors
from sqlalchemy import func

api = Blueprint("admin_dist_type_api", __name__, url_prefix="/api/admin/dist_type")


@api.route("/list", methods=["GET"])
@decorators.login_required
@decorators.only_admins
def list():
    dist_type = DistributionType.query.all()
    dist_type = [d.serialize() for d in dist_type]
    return jsonify(dict(status="success", distribution_types=dist_type))


@api.route("/add", methods=["POST"])
@decorators.login_required
@decorators.only_admins
def add():
    data = request.json or request.data or request.form
    res_code = 200
    res = dict(status="fail")
    name = data.get("name")
    description = data.get("description")
    query = DistributionType.query.filter(
        func.lower(DistributionType.name) == func.lower(name)
    )
    if query.count() > 0:
        res["statusText"] = errors.CUSTOM_ERROR.text
        res["statusData"] = errors.CUSTOM_ERROR.type(
            "Distribution Type of this name already exists"
        )
        return jsonify(res), res_code
    dist_type = DistributionType(name=name, description=description)
    db.session.add(dist_type)
    db.session.commit()
    res["status"] = "success"
    res["dist_type"] = dist_type.serialize()
    return jsonify(res)
