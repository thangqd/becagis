searchTerm = "becagistools"
print([a.id() for a in QgsApplication.processingRegistry().algorithms() if searchTerm in a.id()])
from becagistools.expressions import antipode
print(antipode.function(10.784229903855978, 106.70356815497277,None,None))