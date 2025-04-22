class ProjectSymLinkException(Exception):
  "General exception during project symlink attempt"

class ProjectSymLinkFailure(ProjectSymLinkException):
  "Unrecoverable failure during project symlink attempt"

class ProjectSymLinkExists(ProjectSymLinkException):
  "SymLink Failed because symlink location already exists"

class ProjectAlreadySymLinked(ProjectSymLinkException):
  "SymLink already exists in the requested configuration"

class ProjectSymlinkedElsewhere(ProjectSymLinkException):
  "Project is symlinked already, elsewhere in the symlink directory path"

class ProjectAlreadyExists(Exception):
  "Project could not be created as it already exists"