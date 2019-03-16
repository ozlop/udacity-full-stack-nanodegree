import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Phylum, Class, Order, Family , Genus, Species, PhylumClass, ClassOrder, OrderFamily, FamilyGenus, GenusSpecies


engine = create_engine('sqlite:///fungusamongus.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Load Admin User
session.query(User).delete()
session.commit()

admin = User()
admin.user_id = 1
admin.user_name = 'admin'
admin.user_email = 'admin@fungusamongus.com'
session.add(admin)
session.commit()

# Load Phylum
session.query(Phylum).delete()
session.commit()
phylums = open('phylum.json')
phylum_data = json.load(phylums)


for phylum in phylum_data:
    phylum_entry = Phylum()
    phylum_entry.phylum_name = phylum['PhylumName']
    phylum_entry.phylum_image = phylum['PhylumImage']
    phylum_entry.phylum_description = phylum['PhylumSummary']
    phylum_entry.created_by = 1
    session.add(phylum_entry)
session.commit()

# Load Classes
session.query(Class).delete()
session.commit()

classes = open('class.json')
class_data = json.load(classes)

for clss in class_data:
    class_entry = Class()
    class_entry.class_name = clss['ClassName']
    class_entry.class_image = clss['ClassImage']
    class_entry.class_description = clss['ClassSummary']
    class_entry.created_by = 1
    session.add(class_entry)
session.commit()

session.query(Order).delete()
session.commit()

orders = open('order.json')
order_data = json.load(orders)


for order in order_data:
    order_entry = Order()
    order_entry.order_name = order['OrderName']
    order_entry.order_image = order['OrderImage']
    order_entry.order_description = order['OrderSummary']
    order_entry.created_by = 1
    session.add(order_entry)
session.commit()


session.query(Family).delete()
session.commit()

families = open('family.json')
family_data = json.load(families)

for family in family_data:
    family_entry = Family()
    family_entry.family_name = family['FamilyName']
    family_entry.family_image = family['FamilyImage']
    family_entry.family_description = family['FamilySummary']
    family_entry.created_by = 1
    session.add(family_entry)
session.commit()


session.query(Genus).delete()
session.commit()

genera = open('genus.json')
genera_data = json.load(genera)

for genus in genera_data:
    genus_entry = Genus()
    genus_entry.genus_name = genus['GenusName']
    genus_entry.genus_image = genus['GenusImage']
    genus_entry.genus_description = genus['GenusSummary']
    genus_entry.created_by = 1
    session.add(genus_entry)

session.commit()

session.query(Species).delete()
session.commit()


species = open('species.json')
species_data = json.load(species)

for specie in species_data:
    species_entry = Species()
    species_entry.species_name = specie['SpeciesName']
    species_entry.species_image = specie['SpeciesImage']
    species_entry.species_description = specie['SpeciesSummary']
    species_entry.created_by = 1
    session.add(species_entry)

session.commit()



# relationships

taxon_models = {
    'phylum': Phylum(),
    'class': Class(),
    'order': Order(),
    'family': Family(),
    'genus': Genus(),
    'species': Species()
    }

session.query(PhylumClass).delete()
session.query(ClassOrder).delete()
session.query(OrderFamily).delete()
session.query(FamilyGenus).delete()
session.query(GenusSpecies).delete()

relationships = open('relationships.json')
relationships_data = json.load(relationships)

for relationship in relationships_data:
    try:
        if relationship['parentType'] == 'phylum' and relationship['childType'] == 'class':
            phylum = session.query(Phylum).filter_by(phylum_name=relationship['parent']).one()
            clss = session.query(Class).filter_by(class_name=relationship['child']).one()

            new_relationship = PhylumClass()
            new_relationship.phylum_id = phylum.phylum_id
            new_relationship.class_id = clss.class_id
            new_relationship.created_by = 1

        elif relationship['parentType'] == 'class' and relationship['childType'] == 'order':
            clss = session.query(Class).filter_by(class_name=relationship['parent']).one()
            order = session.query(Order).filter_by(order_name=relationship['child']).one()

            new_relationship = ClassOrder()
            new_relationship.class_id = clss.class_id
            new_relationship.order_id = order.order_id
            new_relationship.created_by = 1

        elif relationship['parentType'] == 'order' and relationship['childType'] == 'family':
            order = session.query(Order).filter_by(order_name=relationship['parent']).one()
            family = session.query(Family).filter_by(family_name=relationship['child']).one()

            new_relationship = OrderFamily()
            new_relationship.order_id = order.order_id
            new_relationship.family_id = family.family_id
            new_relationship.created_by = 1

        elif relationship['parentType'] == 'family' and relationship['childType'] == 'genus':
            family = session.query(Family).filter_by(family_name=relationship['parent']).one()
            genus = session.query(Genus).filter_by(genus_name=relationship['child']).one()

            new_relationship = FamilyGenus()
            new_relationship.family_id = family.family_id
            new_relationship.genus_id = genus.genus_id
            new_relationship.created_by = 1

        elif relationship['parentType'] == 'genus' and relationship['childType'] == 'species':
            genus = session.query(Genus).filter_by(genus_name=relationship['parent']).one()
            species = session.query(Species).filter_by(species_name=relationship['child']).one()

            new_relationship = GenusSpecies()
            new_relationship.genus_id = genus.genus_id
            new_relationship.species_id = species.species_id
            new_relationship.created_by = 1

        session.add(new_relationship)
        session.commit()
    except:
        pass
