

def subbasins(gf):
    """
    Aggregates ocean regions into the following larger sub-basins:
    * Arctic Ocean Basin
    * North Atlantic Basin
    * South Atlantic Basin
    * North Pacific Basin
    * South Pacific Basin
    * Indian Ocean Basin
    * Southern Ocean Basin

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features
    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with ocean sub-basins
    """
    # Authors
    # -------
    # Milena Veneziani

    author = 'Milena Veneziani'

    # Create Arctic Ocean
    fcAr = gf.read('ocean', 'region', ['Central Arctic'])
    fcESS = gf.read('ocean', 'region', ['East Siberian Sea'])
    fcLap = gf.read('ocean', 'region', ['Laptev Sea'])
    fcChu = gf.read('ocean', 'region', ['Chukchi Sea'])
    fcCa = gf.read('ocean', 'region', ['Canada Basin'])
    fcKara = gf.read('ocean', 'region', ['Kara Sea'])
    fcBarents = gf.read('ocean', 'region', ['Barents Sea'])
    fcAr.merge(fcESS)
    fcAr.merge(fcLap)
    fcAr.merge(fcChu)
    fcAr.merge(fcCa)
    fcAr.merge(fcKara)
    fcAr.merge(fcBarents)
    fcAr = fcAr.combine('Arctic Ocean Basin')
    props = fcAr.features[0]['properties']
    props['tags'] = ['Arctic_Ocean_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create North Atlantic
    fcNA = gf.read('ocean', 'region', ['North Atlantic Ocean'])
    fcGS = gf.read('ocean', 'region', ['Greenland Sea'])
    fcLab = gf.read('ocean', 'region', ['Labrador Sea'])
    fcNor = gf.read('ocean', 'region', ['Norwegian Sea'])
    fcIrm = gf.read('ocean', 'region', ['Irminger Sea'])
    fcBayFundy = gf.read('ocean', 'region', ['Bay of Fundy'])
    fcNorthSea = gf.read('ocean', 'region', ['North Sea'])
    fcBaltic = gf.read('ocean', 'region', ['Baltic Sea'])
    fcEngCh = gf.read('ocean', 'region', ['English Channel'])
    fcCeltic = gf.read('ocean', 'region', ['Celtic Sea'])
    fcBristol = gf.read('ocean', 'region', ['Bristol Channel'])
    fcScot = gf.read('ocean', 'region',
                     ['Inner Seas off the West Coast of Scotland'])
    fcIrish = gf.read('ocean', 'region', ['Irish Sea and St Georges Channel'])
    fcBothnia = gf.read('ocean', 'region', ['Gulf of Bothnia'])
    fcCanArc = gf.read('ocean', 'region', ['Canadian Archipelago'])
    fcHudson = gf.read('ocean', 'region', ['Hudson Bay'])
    fcBaffin = gf.read('ocean', 'region', ['Baffin Bay'])
    fcBayBiscay = gf.read('ocean', 'region', ['Bay of Biscay'])
    fcGStLaw = gf.read('ocean', 'region', ['Gulf of St-Lawrence'])
    fcGMexico = gf.read('ocean', 'region', ['Gulf of Mexico'])
    fcCarr = gf.read('ocean', 'region', ['Caribbean Sea'])
    fcGuinea = gf.read('ocean', 'region', ['Gulf of Guinea'])
    fcNA.merge(fcGS)
    fcNA.merge(fcLab)
    fcNA.merge(fcNor)
    fcNA.merge(fcIrm)
    fcNA.merge(fcBayFundy)
    fcNA.merge(fcNorthSea)
    fcNA.merge(fcBaltic)
    fcNA.merge(fcEngCh)
    fcNA.merge(fcCeltic)
    fcNA.merge(fcBristol)
    fcNA.merge(fcScot)
    fcNA.merge(fcIrish)
    fcNA.merge(fcBothnia)
    fcNA.merge(fcCanArc)
    fcNA.merge(fcHudson)
    fcNA.merge(fcBaffin)
    fcNA.merge(fcBayBiscay)
    fcNA.merge(fcGStLaw)
    fcNA.merge(fcGMexico)
    fcNA.merge(fcCarr)
    fcNA.merge(fcGuinea)
    fcNA = fcNA.combine('North Atlantic Basin')
    props = fcNA.features[0]['properties']
    props['tags'] = ['North_Atlantic_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create South Atlantic
    fcSA = gf.read('ocean', 'region', ['South Atlantic Ocean'])
    fcRio = gf.read('ocean', 'region', ['Rio de La Plata'])
    fcSA.merge(fcRio)
    fcSA = fcSA.combine('South Atlantic Basin')
    props = fcSA.features[0]['properties']
    props['tags'] = ['South_Atlantic_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create North Pacific
    fcNP = gf.read('ocean', 'region', ['North Pacific Ocean'])
    fcECS = gf.read('ocean', 'region', ['Eastern China Sea'])
    fcAla = gf.read('ocean', 'region', ['Gulf of Alaska'])
    fcAla2 = gf.read('ocean', 'region',
                     ['The Coastal Waters of Southeast Alaska and British '
                      'Columbia'])
    fcHala = gf.read('ocean', 'region', ['Halamahera Sea'])
    fcYell = gf.read('ocean', 'region', ['Yellow Sea'])
    fcSCS = gf.read('ocean', 'region', ['South China Sea'])
    fcThai = gf.read('ocean', 'region', ['Gulf of Thailand'])
    fcBering = gf.read('ocean', 'region', ['Bering Sea'])
    fcGCali = gf.read('ocean', 'region', ['Gulf of California'])
    fcJapan = gf.read('ocean', 'region', ['Japan Sea'])
    fcSeaOk = gf.read('ocean', 'region', ['Sea of Okhotsk'])
    fcSingapore = gf.read('ocean', 'region', ['Singapore Strait'])
    fcPhil = gf.read('ocean', 'region', ['Philippine Sea'])
    fcSulu = gf.read('ocean', 'region', ['Sulu Sea'])
    fcInland = gf.read('ocean', 'region', ['Inland Sea'])
    fcCelebes = gf.read('ocean', 'region', ['Celebes Sea'])
    fcNP.merge(fcECS)
    fcNP.merge(fcAla)
    fcNP.merge(fcAla2)
    fcNP.merge(fcHala)
    fcNP.merge(fcYell)
    fcNP.merge(fcSCS)
    fcNP.merge(fcThai)
    fcNP.merge(fcBering)
    fcNP.merge(fcGCali)
    fcNP.merge(fcJapan)
    fcNP.merge(fcSeaOk)
    fcNP.merge(fcSingapore)
    fcNP.merge(fcPhil)
    fcNP.merge(fcSulu)
    fcNP.merge(fcInland)
    fcNP.merge(fcCelebes)
    fcNP = fcNP.combine('North Pacific Basin')
    props = fcNP.features[0]['properties']
    props['tags'] = ['North_Pacific_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create South Pacific
    fcSP = gf.read('ocean', 'region', ['South Pacific Ocean'])
    fcBali = gf.read('ocean', 'region', ['Bali Sea'])
    fcSavu = gf.read('ocean', 'region', ['Savu Sea'])
    fcMak = gf.read('ocean', 'region', ['Makassar Strait'])
    fcAra = gf.read('ocean', 'region', ['Arafura Sea'])
    fcCeram = gf.read('ocean', 'region', ['Ceram Sea'])
    fcBis = gf.read('ocean', 'region', ['Bismarck Sea'])
    fcSolo = gf.read('ocean', 'region', ['Solomon Sea'])
    fcMol = gf.read('ocean', 'region', ['Molukka Sea'])
    fcBanda = gf.read('ocean', 'region', ['Banda Sea'])
    fcGBoni = gf.read('ocean', 'region', ['Gulf of Boni'])
    fcGTomini = gf.read('ocean', 'region', ['Gulf of Tomini'])
    fcJava = gf.read('ocean', 'region', ['Java Sea'])
    fcFlores = gf.read('ocean', 'region', ['Flores Sea'])
    fcTimor = gf.read('ocean', 'region', ['Timor Sea'])
    fcTasmanN = gf.read('ocean', 'region', ['Tasman Sea North'])
    fcCoral = gf.read('ocean', 'region', ['Coral Sea'])
    fcSP.merge(fcBali)
    fcSP.merge(fcSavu)
    fcSP.merge(fcMak)
    fcSP.merge(fcAra)
    fcSP.merge(fcCeram)
    fcSP.merge(fcBis)
    fcSP.merge(fcSolo)
    fcSP.merge(fcMol)
    fcSP.merge(fcBanda)
    fcSP.merge(fcGBoni)
    fcSP.merge(fcGTomini)
    fcSP.merge(fcJava)
    fcSP.merge(fcFlores)
    fcSP.merge(fcTimor)
    fcSP.merge(fcTasmanN)
    fcSP.merge(fcCoral)
    fcSP = fcSP.combine('South Pacific Basin')
    props = fcSP.features[0]['properties']
    props['tags'] = ['South_Pacific_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create Indian Ocean
    fcI = gf.read('ocean', 'region', ['Indian Ocean'])
    fcBassStN = gf.read('ocean', 'region', ['Bass Strait North'])
    fcBayBengal = gf.read('ocean', 'region', ['Bay of Bengal'])
    fcGulfOman = gf.read('ocean', 'region', ['Gulf of Oman'])
    fcMalaccaSt = gf.read('ocean', 'region', ['Malacca Strait'])
    fcGABN = gf.read('ocean', 'region', ['Great Australian Bight North'])
    fcMoz = gf.read('ocean', 'region', ['Mozambique Channel'])
    fcBu = gf.read('ocean', 'region', ['Andaman or Burma Sea'])
    fcAden = gf.read('ocean', 'region', ['Gulf of Aden'])
    fcLacc = gf.read('ocean', 'region', ['Laccadive Sea'])
    fcArab = gf.read('ocean', 'region', ['Arabian Sea'])
    fcI.merge(fcBassStN)
    fcI.merge(fcBayBengal)
    fcI.merge(fcGulfOman)
    fcI.merge(fcMalaccaSt)
    fcI.merge(fcGABN)
    fcI.merge(fcMoz)
    fcI.merge(fcBu)
    fcI.merge(fcAden)
    fcI.merge(fcLacc)
    fcI.merge(fcArab)
    fcI = fcI.combine('Indian Ocean Basin')
    props = fcI.features[0]['properties']
    props['tags'] = ['Indian_Ocean_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create Southern Ocean
    fcSO = gf.read('ocean', 'region', ['Southern Ocean'])
    fcTasmanS = gf.read('ocean', 'region', ['Tasman Sea South'])
    fcBassStS = gf.read('ocean', 'region', ['Bass Strait South'])
    fcGABS = gf.read('ocean', 'region', ['Great Australian Bight South'])
    fcSO.merge(fcTasmanS)
    fcSO.merge(fcBassStS)
    fcSO.merge(fcGABS)
    fcSO = fcSO.combine('Southern Ocean Basin')
    props = fcSO.features[0]['properties']
    props['tags'] = ['South_Ocean_Basin', 'oceanSubBasinRegions']
    props['author'] = author

    # Create Ocean subBasins merged feature
    fc = fcSO
    fc.merge(fcAr)
    fc.merge(fcNA)
    fc.merge(fcSA)
    fc.merge(fcNP)
    fc.merge(fcSP)
    fc.merge(fcI)
    props = fc.features[0]['properties']
    props['tags'] = 'oceanSubBasinRegions'
    props['author'] = author

    return fc
