//GLSL
#version 110
#extension ARB_draw_instanced : enable
#extension GL_EXT_draw_instanced : enable

uniform float time;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D height;
uniform sampler2D grass;
uniform vec2 uv_offset;

varying float mask;
varying vec3 normal;


void main()
    {   
    gl_TexCoord[0] = gl_MultiTexCoord0; 
    normal = normalize(gl_NormalMatrix * gl_Normal); 
    int id=gl_InstanceID;    
    float offset=0.0;
    while (id>15)
            {
            offset+=16.0;
            id-=16;
            }
    vec4 v = vec4(gl_Vertex);        
    v.x +=float(id)*16.0;    
    v.y +=offset;
    vec2 uv=vec2(v.x/512.0, v.y/512.0)+uv_offset;

    // Set the mask to discard in the fragment shader
    mask = texture2DLod(grass,uv, 0.0).r;

    float animation =sin(0.7*time+float(gl_InstanceID))*sin(1.7*time+float(gl_InstanceID))*gl_Color.r;
    float h= texture2DLod(height,uv, 0.0).r;    
    v.x += animation;    
    v.y += animation;
    v.z+=h*128.0;
    gl_Position = p3d_ModelViewProjectionMatrix * v;     
        
    }