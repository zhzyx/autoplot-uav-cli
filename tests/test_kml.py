import os
import pytest
from kml.placemark import Placemark
from kml.kml import KML
from kml.action_group import ActionGroup
from kml.action import TakePhotoAction

@pytest.fixture
def setup_kml_template():
    t = KML()
    p = Placemark((1, 2), 0, 5.0, 5.0)
    ag = ActionGroup(1)
    action = TakePhotoAction(0, file_suffix='justsimplesuffix_')
    ag.add_action(action)
    p_1 = Placemark((2, 3), 1, 5.0, 5.0, gimbal_pitch_angle=94)
    p_1.action_group = ag
    t.add_placemark(p)
    t.add_placemark(p_1)
    return t

def test_save_xml(setup_kml_template):
    t = setup_kml_template
    t.save_xml('test.kml')
    assert os.path.exists('test.kml')
    os.remove('test.kml')

def test_save_kmz(setup_kml_template):
    t = setup_kml_template
    t.save_kmz('test.kmz')
    assert os.path.exists('test.kmz')
    os.remove('test.kmz')