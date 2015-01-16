//GLSL
#version 110

uniform sampler2D p3d_Texture0; //rgb color texture 
//uniform sampler2D p3d_Texture1; //normal map

varying float mask;
varying vec3 normal;
//varying vec3 tangent;
//varying vec3 binormal;
varying float fogFactor;

uniform vec4 fog;
uniform vec4 ambient;

void main()
    {    
    if(mask < 0.5)
        discard;               
    else
        {
        vec2 texUV=gl_TexCoord[0].xy;  
        vec4 color_tex=texture2DLod(p3d_Texture0,texUV,0.0);
        //if(fogFactor > 0.5)        
            color_tex.a+=1.9*fogFactor;
            
        //vec4 normap=texture2D(p3d_Texture1,texUV);        
        //float gloss=5.0*normap.a;
        //normap*=2.0;
        //normap-=1.0;        
        //normal.xyz *= normap.z;
        //normal.xyz += tangent * normap.x;
        //normal.xyz += binormal * normap.y;    
        vec3 norm = normalize(normal);  
       

        //lights
        vec4 color =vec4(0.1, 0.15, 0.1, 1.0)+ambient;    
        //directional =sun
        vec3 lightDir,halfV;
        float NdotL, NdotHV; 
        lightDir = vec3(gl_LightSource[0].position); 
        //halfV = gl_LightSource[0].halfVector.xyz;    
        NdotL = max(dot(norm,lightDir),0.0);
        if (NdotL > 0.0)
            {
           NdotHV = max(dot(norm,halfV),0.0);
           color += gl_LightSource[0].diffuse* NdotL;        
           //color +=pow(NdotHV,200.0)*gloss;
           }
      

        vec4 final = vec4(color.rgb *color_tex.rgb, color_tex.a);
        gl_FragData[0] = mix(final,fog ,fogFactor);
        gl_FragData[1]=vec4(fogFactor*color_tex.a, 0.0,0.0,0.0);
        }
    }
    