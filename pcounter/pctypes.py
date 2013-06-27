# codign: utf-8

# Reference:
#  http://stackoverflow.com/a/1695250 
def enum(*seq, **named):
  enums = dict(list(zip(seq, list(range(len(seq))))), **named)
  return type('Enum', (), enums)


