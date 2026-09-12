"""
Function to aggregate individual Greenland glacier basins. 
Currently only glaciers in the Uummannaq/Disko Bay region 
are supported, but other regions may be added.
"""

def uummannaq_disko(gf):
    """
    Aggregate individual tidewater outlet glacier basins in the 
    Uummannaq/Disko Bay region of GIS.

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with Uummannaq/Disko Bay glacier basins
    """
    # Author
    # -------
    # Alex Hager

    regions = ['UummannaqDisko_EqipSermia',
               'UummannaqDisko_KangerluarsuupSermia',
               'UummannaqDisko_KangerlussuupSermia',
               'UummannaqDisko_KangilernataSermia',
               'UummannaqDisko_Kangilleq',
               'UummannaqDisko_KangilliupSermia_RinkIsbrae',
               'UummannaqDisko_PerlerfiupSermia',
               'UummannaqDisko_SalliarutsipSermia_InngiaIsbrae',
               'UummannaqDisko_SaqqarliupSermia',
               'UummannaqDisko_SermeqAvannarleq.south',
               'UummannaqDisko_SermeqAvannarleq_LilleGletsjer',
               'UummannaqDisko_SermeqAvannarleq.north',
               'UummannaqDisko_SermeqKujalleq_AlianaatsupSermia',
               'UummannaqDisko_SermeqKujalleq_JakobshavnIsbrae',
               'UummannaqDisko_SermeqKujalleq_StoreGletsjer',
               'UummannaqDisko_SermeqSilarleq',
               'UummannaqDisko_Sermilik',
               'UummannaqDisko_UmiammakkuSermia',
               ]

    fc = gf.read(componentName='landice', objectType='region',
                 featureNames=regions)

    return fc
