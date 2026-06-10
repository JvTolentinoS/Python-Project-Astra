import glm

system_obj_dict = {
    "Mercury": {
        "init_position": glm.vec3(28224.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 52.98),
        "mass": 3.30e23,
        "density": 5427,
        "r": 0.4, "g": 0.4, "b": 0.4
    },
    "Venus": {
        "init_position": glm.vec3(56472.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 35.40),
        "mass": 4.86e24,
        "density": 5243,
        "r": 0.7, "g": 0.4, "b": 0.4
    },
    
    # Sistema Terra-Lua
    "Earth": {
        "init_position": glm.vec3(78079.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 30.29),
        "mass": 5.972e24,
        "density": 5514,
        "r": 0.4, "g": 0.4, "b": 0.8
    },
    "Moon": {
        "init_position": glm.vec3(78279.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 31.31),
        "mass": 7.347e22,
        "density": 3340,
        "r": 0.3, "g": 0.3, "b": 0.3
    },      
    
    "Mars": {
        "init_position": glm.vec3(118945.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 26.49),
        "mass": 6.39e23,
        "density": 3933,
        "r": 0.8, "g": 0.4, "b": 0.4
    },
    
    # Sistema Jupiter
    "Jupiter": {
        "init_position": glm.vec3(406315.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 13.73),
        "mass": 1.898e27,
        "density": 1326,
        "r": 0.6, "g": 0.6, "b": 0.4
    },
    "Io": {
        "init_position": glm.vec3(406625.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 29.09),
        "mass": 8.93e22,
        "density": 3528,
        "r": 0.8, "g": 0.8, "b": 0.2
    },
    "Europa": {
        "init_position": glm.vec3(406730.73, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 26.99),
        "mass": 4.80e22,
        "density": 3013,
        "r": 0.7, "g": 0.7, "b": 0.8
    },
    "Ganymede": {
        "init_position": glm.vec3(406966.40, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 24.32),
        "mass": 1.48e23,
        "density": 1936,
        "r": 0.6, "g": 0.6, "b": 0.6
    },
    "Callisto": {
        "init_position": glm.vec3(407445.64, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 21.77),
        "mass": 1.08e23,
        "density": 1834,
        "r": 0.5, "g": 0.4, "b": 0.4
    },
    
    # Sistema Saturno
    "Saturn": {
        "init_position": glm.vec3(747913.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 10.19),
        "mass": 5.683e26,
        "density": 687,
        "r": 0.4, "g": 0.4, "b": 0.2
    },
    "Tethys": {
        "init_position": glm.vec3(748193.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 19.14),
        "mass": 6.17e20,
        "density": 984,
        "r": 0.5, "g": 0.5, "b": 0.5
    },
    "Dione": {
        "init_position": glm.vec3(748253.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 18.25),
        "mass": 1.1e21,
        "density": 1478,
        "r": 0.5, "g": 0.5, "b": 0.5
    },
    "Rhea": {
        "init_position": glm.vec3(748343.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 17.30),
        "mass": 2.3e21,
        "density": 1233,
        "r": 0.6, "g": 0.6, "b": 0.6
    },
    "Titan": {
        "init_position": glm.vec3(748613.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 15.68),
        "mass": 1.3452e23,
        "density": 1880,
        "r": 0.7, "g": 0.6, "b": 0.2
    },
    
    # Sistema Urano
    "Uranus": {
        "init_position": glm.vec3(1501565.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 7.13),
        "mass": 8.681e25,
        "density": 1270,
        "r": 0.2, "g": 0.2, "b": 0.6
    },
    "Ariel": {
        "init_position": glm.vec3(1501741.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 11.23),
        "mass": 1.35e21,
        "density": 1660,
        "r": 0.5, "g": 0.5, "b": 0.5
    },
    "Umbriel": {
        "init_position": glm.vec3(1501776.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 10.87),
        "mass": 1.17e21,
        "density": 1390,
        "r": 0.5, "g": 0.5, "b": 0.5
    },
    "Titania": {
        "init_position": glm.vec3(1501886.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 10.13),
        "mass": 3.52e21,
        "density": 1710,
        "r": 0.6, "g": 0.6, "b": 0.6
    },
    "Oberon": {
        "init_position": glm.vec3(1501958.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 9.84),
        "mass": 3.01e21,
        "density": 1630,
        "r": 0.6, "g": 0.6, "b": 0.6
    },
    
    # Sistema Netuno
    "Neptune": {
        "init_position": glm.vec3(2349165.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 5.48),
        "mass": 1.024e26,
        "density": 1638,
        "r": 0.4, "g": 0.4, "b": 0.6
    },
    "Triton": {
        "init_position": glm.vec3(2349395.00, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 9.71),
        "mass": 2.14e22,
        "density": 2061,
        "r": 0.5, "g": 0.5, "b": 0.6
    },
    
    # Sistema Sol
    "Sun": {
        "init_position": glm.vec3(0.0, 0.0, 0.0),
        "init_velocity": glm.vec3(0.0, 0.0, 0.0),
        "mass": 1.989e30,
        "density": 1410,
        "r": 0.8, "g": 0.8, "b": 0.5,
        "glow": True
    }
}