import pytest

from geometric_features.test import TestCase, loaddatadir
from geometric_features import GeometricFeatures
from geometric_features.aggregation import get_aggregator_by_name, basins, \
    subbasins, antarctic, ice_shelves, ismip6, arctic_ocean, transport, \
    arctic_transport, moc, arctic_seaice, qgreenland, nasa_greenland, ismip6_greenland

@pytest.mark.usefixtures('loaddatadir')
class TestAggregation(TestCase):

    def test_get_aggregator_by_name(self):
        gf = GeometricFeatures()
        names = ['Antarctic Regions', 'Arctic Ocean Regions', 'ISMIP6 Greenland Regions',
                 'NASA Greenland Regions', 'Arctic Sea Ice Regions', 'Ocean Basins', 
                 'Ice Shelves', 'Ocean Subbasins', 'ISMIP6 Regions', 'MOC Basins', 'Historical Sea Ice',
                 'Transport Transects', 'Arctic Transport Transects']

        for name in names:
            function, prefix, date = get_aggregator_by_name(name)
            function(gf)

    def test_antarctic(self):
        gf = GeometricFeatures()
        antarctic(gf)

    def test_arctic_ocean(self):
        gf = GeometricFeatures()
        arctic_ocean(gf)

    def test_arctic_seaice(self):
        gf = GeometricFeatures()
        arctic_seaice(gf)

    def test_basins(self):
        gf = GeometricFeatures()
        basins(gf)

    def test_ice_shelves(self):
        gf = GeometricFeatures()
        ice_shelves(gf)

    def test_subbasins(self):
        gf = GeometricFeatures()
        subbasins(gf)

    def test_ismip6(self):
        gf = GeometricFeatures()
        ismip6(gf)

    def test_moc(self):
        gf = GeometricFeatures()
        moc(gf)

    def test_transport(self):
        gf = GeometricFeatures()
        transport(gf)

    def test_arctic_transport(self):
        gf = GeometricFeatures()
        arctic_transport(gf)

    def test_qgreenland(self):
        gf = GeometricFeatures()
        qgreenland(gf)
    
    def test_nasa_greenland(self):
        gf = GeometricFeatures()
        nasa_greenland(gf)

    def test_ismip6_greenland(self):
        gf = GeometricFeatures()
        ismip6_greenland(gf)
