from tethys_sdk.base import TethysAppBase


class GreatLakesViewer(TethysAppBase):
    """
    Tethys app class for Great Lakes Viewer.
    """

    name = 'Great Lakes Viewer'
    description = ''
    package = 'great_lakes_viewer'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/image001.png'
    root_url = 'great-lakes-viewer'
    color = '#2980b9'
    tags = ''
    enable_feedback = False
    feedback_emails = []
