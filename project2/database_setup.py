from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, synonym
from sqlalchemy import create_engine
from datetime import datetime


Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    user_id = Column('UserId', Integer, primary_key=True)
    user_name = Column('UserName', String, nullable=False)
    user_email = Column('UserEmail', String, nullable=False)
    user_picture = Column('UserPicture', String)


class Phylum(Base):
    __tablename__ = 'Phylum'

    phylum_id = Column('PhylumId', Integer, primary_key=True)
    phylum_name = Column('PhylumName', String, nullable=False)
    phylum_image = Column('PhylumImage', String)
    phylum_description = Column('PhylumDescription', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                                  default=datetime.utcnow)

    classes = relationship('Class', secondary='PhylumToClass',
                           back_populates='phylums')

    rank_id = synonym("phylum_id")
    rank_type = 'phylum'
    name = synonym("phylum_name")
    image = synonym("phylum_image")
    description = synonym("phylum_description")
    children = synonym("classes")

    @property
    def serialize(self):
        return {
            'phylumId': self.phylum_id,
            'phylumName': self.phylum_name,
            'childClasses': [clss.class_name for clss in self.classes],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Class(Base):
    __tablename__ = 'Class'

    class_id = Column('ClassId', Integer, primary_key=True)
    class_name = Column('ClassName', String, nullable=False)
    class_image = Column('ClassImage', String)
    class_description = Column('ClassDescription', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                                  default=datetime.utcnow)

    phylums = relationship('Phylum', secondary='PhylumToClass',
                           back_populates='classes')
    orders = relationship('Order', secondary='ClassToOrder',
                           back_populates='classes')

    rank_id = synonym("class_id")
    rank_type = 'class'
    name = synonym("class_name")
    image = synonym("class_image")
    description = synonym("class_description")
    parent = synonym("phylums")
    children = synonym("orders")

    @property
    def serialize(self):
        return {
            'classId': self.class_id,
            'className': self.class_name,
            'childOrders': [order.order_name for order in self.orders],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Order(Base):
    __tablename__ = 'Order'

    order_id = Column('OrderId', Integer, primary_key=True)
    order_name = Column('OrderName', String, nullable=False)
    order_description = Column('OrderDescription', String)
    order_image = Column('OrderImage', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                               default=datetime.utcnow)

    classes = relationship('Class', secondary='ClassToOrder',
                           back_populates='orders')
    families = relationship('Family', secondary='OrderToFamily',
                            back_populates='orders')

    rank_id = synonym("order_id")
    rank_type = 'order'
    name = synonym("order_name")
    image = synonym("order_image")
    description = synonym("order_description")
    parent = synonym("classes")
    children = synonym("families")

    @property
    def serialize(self):
        return {
            'orderId': self.order_id,
            'orderName': self.order_name,
            'childFamilies': [family.family_name for family in self.families],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Family(Base):
    __tablename__ = 'Family'

    family_id = Column('FamilyId', Integer, primary_key=True)
    family_name = Column('FamilyName', String, nullable=False)
    family_description = Column('FamilyDescription', String)
    family_image = Column('FamilyImage', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                                  default=datetime.utcnow)

    orders = relationship('Order', secondary='OrderToFamily',
                            back_populates='families')
    genera = relationship('Genus', secondary='FamilyToGenus',
                            back_populates='families')

    rank_id = synonym("family_id")
    rank_type = 'family'
    name = synonym("family_name")
    image = synonym("family_image")
    description = synonym("family_description")
    parent = synonym("orders")
    children = synonym("genera")

    @property
    def serialize(self):
        return {
            'familyId': self.family_id,
            'famliyName': self.family_name,
            'childGenera': [genus.genus_name for genus in self.genera],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Genus(Base):
    __tablename__ = 'Genus'

    genus_id = Column('GenusId', Integer, primary_key=True)
    genus_name = Column('GenusName', String, nullable=False)
    genus_description = Column('GenusDescription', String)
    genus_image = Column('GenusImage', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                                  default=datetime.utcnow)

    families = relationship('Family', secondary='FamilyToGenus',
                            back_populates='genera')
    species = relationship('Species', secondary='GenusToSpecies',
                           back_populates='genera')

    rank_id = synonym("genus_id")
    rank_type = 'genus'
    name = synonym("genus_name")
    image = synonym("genus_image")
    description = synonym("genus_description")
    parent = synonym("families")
    children = synonym("species")

    @property
    def serialize(self):
        return {
            'genusId': self.phylum_id,
            'genusName': self.phylum_name,
            'childSpecies': [specie.species_name for specie in self.species],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Species(Base):
    __tablename__ = 'Species'

    species_id = Column('SpeciesId', Integer, primary_key=True)
    species_name = Column('SpeciesName', String, nullable=False)
    species_description = Column('SpeciesDescription', String)
    species_image = Column('GenusImage', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                                 default=datetime.utcnow)
    datetime_modified = Column('DatetimeModified', DateTime,
                                  default=datetime.utcnow)

    genera = relationship('Genus', secondary='GenusToSpecies',
                           back_populates='species')
    sightings = relationship('Sighting', secondary='SpeciesToSighting',
                             back_populates='sighting_species')

    rank_id = synonym("species_id")
    rank_type = 'species'
    name = synonym("species_name")
    image = synonym("species_image")
    description = synonym("species_description")
    parent = synonym("genera")
    children = synonym("sightings")

    @property
    def serialize(self):
        return {
            'speciesId': self.species_id,
            'speciesName': self.species_name,
            'sightings': [sighting.serialize for sighting in self.sightings],
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created
        }


class Confirmation(Base):
    __tablename__ = 'Confirmation'

    confirmation_id = Column('ConfirmationId', Integer, primary_key=True)
    confirmation_name = Column('ConfirmationName', String, nullable=False)


class Sighting(Base):
    __tablename__ = 'Sighting'

    sighting_id = Column('SightingId', Integer, primary_key=True)
    phylum_id = Column('PhylumId', Integer, ForeignKey('Phylum.PhylumId'))
    class_id = Column('ClassId', Integer, ForeignKey('Class.ClassId'))
    order_id = Column('OrderId', Integer, ForeignKey('Order.OrderId'))
    family_id = Column('FamilyId', Integer, ForeignKey('Family.FamilyId'))
    genus_id = Column('GenuesId', Integer, ForeignKey('Genus.GenusId'))
    species_id = Column('SpeciesId', Integer, ForeignKey('Species.SpeciesId'))
    sighting_location = Column('SightingLocation', String)
    sighting_comment = Column('SightingComment', String)
    sighting_image = Column('SightingImage', String)
    sighting_confirmation = Column('MushroomConfirmation', Integer,
                                   ForeignKey('Confirmation.ConfirmationId'))
    sighting_image = Column('SightingImage', String)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)
    modified_by = Column('ModifiedBy', Integer, ForeignKey('User.UserId'))
    datetime_modified = Column('DatetimeModified', DateTime,
                               default=datetime.utcnow)
    confirmed_by = Column('ConfirmedBy', Integer, ForeignKey('User.UserId'))
    datetime_confirmed = Column('DatetimeConfirmed', DateTime,
                                default=datetime.utcnow)

    sighting_phylum = relationship('Phylum')
    sighting_class = relationship('Class')
    sighting_order = relationship('Order')
    sighting_family = relationship('Family')
    sighting_genus = relationship('Genus')
    sighting_species = relationship('Species')

    @property
    def serialize(self):
        return {
            'sightingId': self.sighting_id,
            'sightingPhylumId': self.phylum_id,
            'sightingClassId': self.class_id,
            'sightingOrderId': self.order_id,
            'sightingFamilyId': self.family_id,
            'sightingGenusId': self.genus_id,
            'sightingSpeciesId': self.species_id,
            'sightingLocation': self.location,
            'sightingComment': self.comment,
            'sightingImage': self.image,
            'createdBy': self.created_by,
            'datetimeCreated': self.datetime_created,
            'modifiedBy': self.created_by,
            'datetimeModified': self.datetime_created
        }


class PhylumClass(Base):
    __tablename__ = 'PhylumToClass'
    phylum_id = Column('PhylumId', Integer,
                       ForeignKey('Phylum.PhylumId'),
                       primary_key=True)
    class_id = Column('ClassId', Integer,
                      ForeignKey('Class.ClassId'),
                      primary_key=True)
    created_by = Column('CreatedBy', Integer,
                        ForeignKey('User.UserId'),
                        primary_key=True)
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)


class ClassOrder(Base):
    __tablename__ = 'ClassToOrder'
    class_id = Column('ClassId', Integer, ForeignKey('Class.ClassId'),
                      primary_key=True)
    order_id = Column('OrderId', Integer, ForeignKey('Order.OrderId'),
                      primary_key=True)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)
    modified_by = Column('ModifiedBy', Integer, ForeignKey('User.UserId'))
    datetime_modified = Column('DateTimeModified', DateTime,
                               default=datetime.utcnow)


class OrderFamily(Base):
    __tablename__ = 'OrderToFamily'
    order_id = Column('OrderId', Integer, ForeignKey('Order.OrderId'),
                      primary_key=True)
    family_id = Column('FamilyId', Integer, ForeignKey('Family.FamilyId'),
                       primary_key=True)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)
    modified_by = Column('ModifiedBy', Integer, ForeignKey('User.UserId'))
    datetime_modified = Column('DateTimeModified', DateTime,
                               default=datetime.utcnow)


class FamilyGenus(Base):
    __tablename__ = 'FamilyToGenus'
    family_id = Column('FamilyId', Integer, ForeignKey('Family.FamilyId'),
                       primary_key=True)
    genus_id = Column('GenusId', Integer, ForeignKey('Genus.GenusId'),
                      primary_key=True)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)
    modified_by = Column('ModifiedBy', Integer, ForeignKey('User.UserId'))
    datetime_modified = Column('DateTimeModified', DateTime,
                               default=datetime.utcnow)


class GenusSpecies(Base):
    __tablename__ = 'GenusToSpecies'
    genus_id = Column('GenusId', Integer, ForeignKey('Genus.GenusId'),
                      primary_key=True)
    species_id = Column('SpeciesId', Integer, ForeignKey('Species.SpeciesId'),
                        primary_key=True)
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)
    modified_by = Column('ModifiedBy', Integer, ForeignKey('User.UserId'))
    datetime_modified = Column('DateTimeModified', DateTime,
                               default=datetime.utcnow)


class SpeciesSighting(Base):
    __tablename__ = 'SpeciesToSighting'
    sighting_id = Column('SightingId', Integer, ForeignKey('Sighting.SightingId'),
                      primary_key=True)
    species_id = Column('SpeciesId', Integer, ForeignKey('Species.SpeciesId'))
    created_by = Column('CreatedBy', Integer, ForeignKey('User.UserId'))
    datetime_created = Column('DatetimeCreated', DateTime,
                              default=datetime.utcnow)


engine = create_engine('sqlite:///fungusamongus.db')

Base.metadata.create_all(engine)
