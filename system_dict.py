import glm

# system_obj_dict = {
#     "Charon": {
#         "_init_position": glm.vec3(9.11, 0.0, 0.0),
#         "_init_velocity": glm.vec3(0.0, 0.0, -0.1986),
#         "_mass": 1.586e21,
#         "_density": 1702,
#         "_color": (0.6, 0.6, 0.7)
#     },
#     "Pluto": {
#         "_init_position": glm.vec3(-1.11, 0.0, 0.0),
#         "_init_velocity": glm.vec3(0.0, 0.0, 0.0242),
#         "_mass": 1.303e22,
#         "_density": 1854,
#         "_color": (0.75, 0.55, 0.45)
#     },
# }
system_obj_dict = {
    "Mercury": {
        "_init_position": glm.vec3(28224.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 52.98),
        "_mass": 3.30e23,
        "_density": 5427,
        "_color": ( 0.4,  0.4,  0.4 )
    },
    "Venus": {
        "_init_position": glm.vec3(56472.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 35.40),
        "_mass": 4.86e24,
        "_density": 5243,
        "_color": ( 0.7,  0.4,  0.4 )
    },
    
    # Sistema Terra-Lua
    # -----------------
    "Earth": {
        "_init_position": glm.vec3(78079.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 30.29),
        "_mass": 5.972e24,
        "_density": 5514,
        "_color": ( 0.4,  0.4,  0.8 )
    },
    "Moon": {
        "_init_position": glm.vec3(78279.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 31.31),
        "_mass": 7.347e22,
        "_density": 3340,
        "_color": ( 0.3,  0.3,  0.3 )
    },      
    
    "Mars": {
        "_init_position": glm.vec3(118945.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 26.49),
        "_mass": 6.39e23,
        "_density": 3933,
        "_color": ( 0.8,  0.4,  0.4 )
    },
    
    # Sistema Jupiter
    # ---------------
    "Jupiter": {
        "_init_position": glm.vec3(406315.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 13.73),
        "_mass": 1.898e27,
        "_density": 1326,
        "_color": ( 0.6,  0.6,  0.4 )
    },
    "Europa": {
        "_init_position": glm.vec3(406730.73, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 26.99),
        "_mass": 4.80e22,
        "_density": 3013,
        "_color": ( 0.7,  0.7,  0.8 )
    },
    "Ganymede": {
        "_init_position": glm.vec3(406966.40, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 24.32),
        "_mass": 1.48e23,
        "_density": 1936,
        "_color": ( 0.6,  0.6,  0.6 )
    },
    "Callisto": {
        "_init_position": glm.vec3(407445.64, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 21.77),
        "_mass": 1.08e23,
        "_density": 1834,
        "_color": ( 0.5,  0.4,  0.4 )
    },
    
    # Sistema Saturno
    # ---------------
    "Saturn": {
        "_init_position": glm.vec3(747913.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 10.19),
        "_mass": 5.683e26,
        "_density": 687,
        "_color": ( 0.4,  0.4,  0.2 )
    },
    "Tethys": {
        "_init_position": glm.vec3(748193.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 19.14),
        "_mass": 6.17e20,
        "_density": 984,
        "_color": ( 0.5,  0.5,  0.5 )
    },
    "Dione": {
        "_init_position": glm.vec3(748253.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 18.25),
        "_mass": 1.1e21,
        "_density": 1478,
        "_color": ( 0.5,  0.5,  0.5 )
    },
    "Rhea": {
        "_init_position": glm.vec3(748343.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 17.30),
        "_mass": 2.3e21,
        "_density": 1233,
        "_color": ( 0.6,  0.6,  0.6 )
    },
    "Titan": {
        "_init_position": glm.vec3(748613.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 15.68),
        "_mass": 1.3452e23,
        "_density": 1880,
        "_color": ( 0.7,  0.6,  0.2 )
    },
    
    # Sistema Urano
    # -------------

    "Uranus": {
        "_init_position": glm.vec3(1501565.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 7.13),
        "_mass": 8.681e25,
        "_density": 1270,
        "_color": ( 0.2,  0.2,  0.6 )
    },
    "Ariel": {
        "_init_position": glm.vec3(1501741.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 11.23),
        "_mass": 1.35e21,
        "_density": 1660,
        "_color": ( 0.5,  0.5,  0.5 )
    },
    "Umbriel": {
        "_init_position": glm.vec3(1501776.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 10.87),
        "_mass": 1.17e21,
        "_density": 1390,
        "_color": ( 0.5,  0.5,  0.5 )
    },
    "Titania": {
        "_init_position": glm.vec3(1501886.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 10.13),
        "_mass": 3.52e21,
        "_density": 1710,
        "_color": ( 0.6,  0.6,  0.6 )
    },
    "Oberon": {
        "_init_position": glm.vec3(1501958.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 9.84),
        "_mass": 3.01e21,
        "_density": 1630,
        "_color": ( 0.6,  0.6,  0.6 )
    },
    
    # Sistema Netuno
    # --------------
    "Neptune": {
        "_init_position": glm.vec3(2349165.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 5.48),
        "_mass": 1.024e26,
        "_density": 1638,
        "_color": ( 0.4,  0.4,  0.6 )
    },
    "Triton": {
        "_init_position": glm.vec3(2349395.00, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 9.71),
        "_mass": 2.14e22,
        "_density": 2061,
        "_color": ( 0.5,  0.5,  0.6 )
    },
    
    # Sistema Sol
    # -----------
    "Sun": {
        "_init_position": glm.vec3(0.0, 0.0, 0.0),
        "_init_velocity": glm.vec3(0.0, 0.0, 0.0),
        "_mass": 1.989e30,
        "_density": 1410,
        "_color": ( 0.8,  0.8,  0.5, ),
        "_glow": True
    }
}

# system_obj_dict = {
#     "Alpha_Centauri_A": {
#         "_init_position": glm.vec3(754.2, 0.0, 0.0),
#         "_init_velocity": glm.vec3(0.0, 0.0, 6.97),
#         "_mass": 2.1879e30,
#         "_density": 897.0,
#         "_color": (0.8, 0.8, 0.5),
#         "_glow": True
#     },
#     "Alpha_Centauri_B": {
#         "_init_position": glm.vec3(-921.8, 0.0, 0.0),
#         "_init_velocity": glm.vec3(0.0, 0.0, -8.53),
#         "_mass": 1.7901e30,
#         "_density": 1995.0,
#         "_color": (0.9, 0.7, 0.4),
#         "_glow": True
#     },
#     "Proxima_Centauri": {
#         "_init_position": glm.vec3(2.99e5, 0.0, 0.0),     
#         "_init_velocity": glm.vec3(0.0, 0.0, 0.97),          
#         "_mass": 2.3868e29,
#         "_density": 50140.0,
#         "_color": (1.0, 0.3, 0.3),
#         "_glow": True
#     }
# }