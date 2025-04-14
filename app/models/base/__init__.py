from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to register them with Base
from .team import *
from .course import *
from .league import *
from .match import *