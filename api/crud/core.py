from api.models import Branch, Session


def start_session(branch: Branch, session: Session):
    # create a BranchSessionAssociation entry and activate it
    # close any existing active session
    pass


def end_session(branch: Branch, session: Session):
    pass
