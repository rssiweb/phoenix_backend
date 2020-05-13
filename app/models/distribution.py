from app import db
from .base import Base, Faculty
from sqlalchemy.orm import relationship, backref


class DistributionItemType(Base):
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=True)

    items = relationship("DistributionItem", back_populates="item_type")


class DistributionItem(Base):
    name = db.Column(db.String(50), nullable=False, unique=True)
    item_type_id = db.Column(
        db.Integer, db.ForeignKey("distribution_item_type.id"), nullable=False
    )
    item_type = relationship("DistributionItemType", back_populates="items")

    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(500), nullable=True)

    distributions = relationship("Distribution", back_populates="distribution_item")


class DistributionType(Base):
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=True)

    distributions = relationship("Distribution", back_populates="distribution_type")

    def serialize(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            created_on=self.date_created,
        )


class Distribution(Base):
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    branch = relationship("Branch", back_populates="distributions")

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    student = relationship("Student", back_populates="distributions")

    distribution_item_id = db.Column(
        db.Integer, db.ForeignKey("distribution_item.id"), nullable=False
    )
    distribution_item = relationship("DistributionItem", back_populates="distributions")

    distribution_type_id = db.Column(
        db.Integer, db.ForeignKey("distribution_type.id"), nullable=False
    )
    distribution_type = relationship("DistributionType", back_populates="distributions")

    recorded_by_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    recorded_by = relationship("Faculty", foreign_keys=[recorded_by_id])

    approved_by_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    approved_by = relationship("Faculty", foreign_keys=[approved_by_id])

    comments = db.Column(db.String(100), nullable=True)
    is_return_entry = db.Column(db.Boolean, nullable=False, default=False)
