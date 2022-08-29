searchTerm = "becagistools"
print([a.id() for a in QgsApplication.processingRegistry().algorithms() if searchTerm in a.id()])