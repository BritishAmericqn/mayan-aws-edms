from mayan.apps.dependencies.classes import PythonDependency

# Research app dependencies for data analysis
PythonDependency(
    module=__name__, name='pandas', version_string='==2.2.0'
)

PythonDependency(
    module=__name__, name='matplotlib', version_string='==3.8.0'
)

PythonDependency(
    module=__name__, name='openpyxl', version_string='==3.1.2'
)

PythonDependency(
    module=__name__, name='reportlab', version_string='==4.0.7'
)

PythonDependency(
    module=__name__, name='numpy', version_string='==1.26.0'
)

