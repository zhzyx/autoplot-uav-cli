"""
Camera coverage utility functions for computing ground coverage based on camera parameters.

This module provides functions to calculate:
- Ground coverage dimensions based on field of view and height
- Coverage area calculations
- Pixel resolution on ground
- Overlap calculations for mission planning
"""

import math
from typing import Tuple, NamedTuple
from dataclasses import dataclass


@dataclass
class CameraParams:
    """Camera parameters for coverage calculations."""
    fov_h: float  # Horizontal field of view in degrees
    fov_v: float  # Vertical field of view in degrees
    sensor_width: float = None  # Sensor width in mm (optional)
    sensor_height: float = None  # Sensor height in mm (optional)
    focal_length: float = None  # Focal length in mm (optional)
    image_width: int = None  # Image width in pixels (optional)
    image_height: int = None  # Image height in pixels (optional)


class CoverageResult(NamedTuple):
    """Result of camera coverage calculation."""
    ground_width: float  # Ground coverage width in meters
    ground_height: float  # Ground coverage height in meters
    area: float  # Coverage area in square meters
    gsd: float  # Ground sample distance in meters per pixel


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return math.radians(degrees)


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(radians)


def calculate_fov_from_focal_length(focal_length: float, sensor_dimension: float) -> float:
    """
    Calculate field of view from focal length and sensor dimension.
    
    Args:
        focal_length: Focal length in mm
        sensor_dimension: Sensor width or height in mm
    
    Returns:
        Field of view in degrees
    """
    fov_rad = 2 * math.atan(sensor_dimension / (2 * focal_length))
    return radians_to_degrees(fov_rad)


def calculate_ground_coverage_from_fov(height: float, fov_h: float, fov_v: float) -> Tuple[float, float]:
    """
    Calculate ground coverage dimensions from height and field of view.
    
    Args:
        height: Camera height above ground in meters
        fov_h: Horizontal field of view in degrees
        fov_v: Vertical field of view in degrees
    
    Returns:
        Tuple of (ground_width, ground_height) in meters
    """
    fov_h_rad = degrees_to_radians(fov_h)
    fov_v_rad = degrees_to_radians(fov_v)
    
    ground_width = 2 * height * math.tan(fov_h_rad / 2)
    ground_height = 2 * height * math.tan(fov_v_rad / 2)
    
    return ground_width, ground_height


def calculate_ground_coverage_from_focal_length(
    height: float, 
    focal_length: float, 
    sensor_width: float, 
    sensor_height: float
) -> Tuple[float, float]:
    """
    Calculate ground coverage from camera height, focal length, and sensor dimensions.
    
    Args:
        height: Camera height above ground in meters
        focal_length: Focal length in mm
        sensor_width: Sensor width in mm
        sensor_height: Sensor height in mm
    
    Returns:
        Tuple of (ground_width, ground_height) in meters
    """
    ground_width = (sensor_width * height) / focal_length
    ground_height = (sensor_height * height) / focal_length
    
    return ground_width, ground_height


def calculate_gsd(height: float, focal_length: float, sensor_dimension: float, image_dimension: int) -> float:
    """
    Calculate Ground Sample Distance (GSD) - the distance between pixel centers on the ground.
    
    Args:
        height: Camera height above ground in meters
        focal_length: Focal length in mm
        sensor_dimension: Sensor width or height in mm
        image_dimension: Image width or height in pixels
    
    Returns:
        GSD in meters per pixel
    """
    pixel_size = sensor_dimension / image_dimension  # mm per pixel
    gsd = (pixel_size * height) / focal_length / 1000  # Convert mm to meters
    return gsd


def calculate_coverage_area(ground_width: float, ground_height: float) -> float:
    """
    Calculate coverage area in square meters.
    
    Args:
        ground_width: Ground coverage width in meters
        ground_height: Ground coverage height in meters
    
    Returns:
        Coverage area in square meters
    """
    return ground_width * ground_height


def calculate_overlap_distance(coverage_dimension: float, overlap_percent: float) -> float:
    """
    Calculate the distance between shots for a given overlap percentage.
    
    Args:
        coverage_dimension: Coverage dimension (width or height) in meters
        overlap_percent: Desired overlap percentage (0-100)
    
    Returns:
        Distance between shots in meters
    """
    overlap_ratio = overlap_percent / 100.0
    return coverage_dimension * (1 - overlap_ratio)


def calculate_required_shots(
    total_distance: float, 
    coverage_dimension: float, 
    overlap_percent: float
) -> int:
    """
    Calculate number of shots required to cover a given distance with specified overlap.
    
    Args:
        total_distance: Total distance to cover in meters
        coverage_dimension: Coverage dimension in the direction of travel in meters
        overlap_percent: Desired overlap percentage (0-100)
    
    Returns:
        Number of shots required
    """
    shot_spacing = calculate_overlap_distance(coverage_dimension, overlap_percent)
    if shot_spacing <= 0:
        raise ValueError("Invalid overlap percentage or coverage dimension")
    
    return math.ceil(total_distance / shot_spacing)


def calculate_full_coverage(camera_params: CameraParams, height: float) -> CoverageResult:
    """
    Calculate comprehensive camera coverage information.
    
    Args:
        camera_params: Camera parameters
        height: Camera height above ground in meters
    
    Returns:
        CoverageResult with ground dimensions, area, and GSD
    """
    # Calculate ground coverage
    ground_width, ground_height = calculate_ground_coverage_from_fov(
        height, camera_params.fov_h, camera_params.fov_v
    )
    
    # Calculate area
    area = calculate_coverage_area(ground_width, ground_height)
    
    # Calculate GSD if enough parameters are provided
    gsd = 0.0
    
    # Try focal length method first (more accurate)
    if (camera_params.focal_length and camera_params.sensor_width and 
        camera_params.image_width):
        gsd = calculate_gsd(
            height, 
            camera_params.focal_length, 
            camera_params.sensor_width, 
            camera_params.image_width
        )
    # Fallback to FOV method
    elif (camera_params.fov_h and camera_params.image_width):
        gsd = calculate_gsd_from_fov(
            height, 
            camera_params.fov_h, 
            camera_params.image_width, 
            is_horizontal=True
        )
    
    return CoverageResult(
        ground_width=ground_width,
        ground_height=ground_height,
        area=area,
        gsd=gsd
    )


def calculate_mission_grid_spacing(
    camera_params: CameraParams, 
    height: float, 
    forward_overlap: float = 80.0,
    side_overlap: float = 60.0
) -> Tuple[float, float]:
    """
    Calculate grid spacing for mission planning with specified overlaps.
    
    Args:
        camera_params: Camera parameters
        height: Camera height above ground in meters
        forward_overlap: Forward overlap percentage (0-100)
        side_overlap: Side overlap percentage (0-100)
    
    Returns:
        Tuple of (forward_spacing, side_spacing) in meters
    """
    ground_width, ground_height = calculate_ground_coverage_from_fov(
        height, camera_params.fov_h, camera_params.fov_v
    )
    
    forward_spacing = calculate_overlap_distance(ground_height, forward_overlap)
    side_spacing = calculate_overlap_distance(ground_width, side_overlap)
    
    return forward_spacing, side_spacing


def altitude_for_target_gsd(
    target_gsd: float, 
    focal_length: float, 
    sensor_dimension: float, 
    image_dimension: int
) -> float:
    """
    Calculate required altitude to achieve target Ground Sample Distance.
    
    Args:
        target_gsd: Target GSD in meters per pixel
        focal_length: Focal length in mm
        sensor_dimension: Sensor width or height in mm
        image_dimension: Image width or height in pixels
    
    Returns:
        Required height above ground in meters
    """
    pixel_size = sensor_dimension / image_dimension  # mm per pixel
    height = (target_gsd * focal_length * 1000) / pixel_size  # Convert meters to mm
    return height


def calculate_gsd_from_fov(
    height: float, 
    fov: float, 
    image_dimension: int, 
    is_horizontal: bool = True
) -> float:
    """
    Calculate Ground Sample Distance (GSD) from field of view and image resolution.
    
    Args:
        height: Camera height above ground in meters
        fov: Field of view in degrees (horizontal or vertical)
        image_dimension: Image dimension in pixels (width for horizontal FOV, height for vertical FOV)
        is_horizontal: Whether the FOV is horizontal (True) or vertical (False)
    
    Returns:
        GSD in meters per pixel
    """
    fov_rad = degrees_to_radians(fov)
    ground_dimension = 2 * height * math.tan(fov_rad / 2)
    gsd = ground_dimension / image_dimension
    return gsd


def calculate_gsd_both_directions(
    height: float, 
    fov_h: float, 
    fov_v: float, 
    image_width: int, 
    image_height: int
) -> Tuple[float, float]:
    """
    Calculate GSD in both horizontal and vertical directions.
    
    Args:
        height: Camera height above ground in meters
        fov_h: Horizontal field of view in degrees
        fov_v: Vertical field of view in degrees
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Tuple of (gsd_horizontal, gsd_vertical) in meters per pixel
    """
    gsd_h = calculate_gsd_from_fov(height, fov_h, image_width, is_horizontal=True)
    gsd_v = calculate_gsd_from_fov(height, fov_v, image_height, is_horizontal=False)
    return gsd_h, gsd_v


def calculate_gsd_from_camera_params(camera_params: CameraParams, height: float) -> Tuple[float, float]:
    """
    Calculate GSD from CameraParams using FOV and resolution.
    
    Args:
        camera_params: Camera parameters including FOV and image dimensions
        height: Camera height above ground in meters
    
    Returns:
        Tuple of (gsd_horizontal, gsd_vertical) in meters per pixel
        Returns (0.0, 0.0) if required parameters are missing
    """
    if not all([camera_params.fov_h, camera_params.fov_v, 
                camera_params.image_width, camera_params.image_height]):
        return 0.0, 0.0
    
    return calculate_gsd_both_directions(
        height, 
        camera_params.fov_h, 
        camera_params.fov_v, 
        camera_params.image_width, 
        camera_params.image_height
    )


# Common camera presets
COMMON_CAMERAS = {
    "dji_mini_3": CameraParams(
        fov_h=82.6, fov_v=75.0,
        sensor_width=9.7, sensor_height=7.3,
        focal_length=6.7,
        image_width=4000, image_height=3000
    ),
    "dji_air_2s": CameraParams(
        fov_h=88.0, fov_v=58.0,
        sensor_width=13.2, sensor_height=8.8,
        focal_length=8.4,
        image_width=5472, image_height=3648
    ),
    "dji_mavic_3": CameraParams(
        fov_h=84.0, fov_v=56.0,
        sensor_width=17.3, sensor_height=13.0,
        focal_length=12.29,
        image_width=5280, image_height=3956
    ),
}


def get_camera_preset(camera_name: str) -> CameraParams:
    """
    Get camera parameters for common camera models.
    
    Args:
        camera_name: Name of the camera model
    
    Returns:
        CameraParams for the specified camera
    
    Raises:
        KeyError: If camera name is not found
    """
    if camera_name.lower() not in COMMON_CAMERAS:
        available = ", ".join(COMMON_CAMERAS.keys())
        raise KeyError(f"Camera '{camera_name}' not found. Available: {available}")
    
    return COMMON_CAMERAS[camera_name.lower()]