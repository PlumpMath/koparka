from panda3d.core import *
import json
from direct.actor.Actor import Actor

def loadModel(file, collision=None, animation=None):
    model=None
    if animation:
        model=Actor(file, animation)                   
        #default anim
        if 'default' in animation:
            model.loop('default')
        elif 'idle' in animation:
            model.loop('idle')
        else: #some random anim
             model.loop(animation.items()[0])
    else:
        model=loader.loadModel(file)
    model.setPythonTag('model_file', file)
    #load shaders
    for geom in model.findAllMatches('**/+GeomNode'):
        if geom.hasTag('cg_shader'):            
            geom.setShader(loader.loadShader("shaders/"+geom.getTag('cg_shader')))
        elif geom.hasTag('glsl_shader'):  
            glsl_shader=geom.getTag('glsl_shader')      
            geom.setShader(Shader.load(Shader.SLGLSL, "shaders/{0}_v.glsl".format(glsl_shader),"shaders/{0}_f.glsl".format(glsl_shader)))
        else:
            #geom.setShader(loader.loadShader("shaders/default.cg"))
            geom.setShader(Shader.load(Shader.SLGLSL, "shaders/default_v.glsl","shaders/default_f.glsl"))
    #collisions        
    model.setCollideMask(BitMask32.allOff())
    if collision:
        coll=loader.loadModel(collision)
        coll.reparentTo(model)
        coll.find('**/collision').setCollideMask(BitMask32.bit(2))        
        coll.find('**/collision').setPythonTag('object', model)
        if animation:
            model.setPythonTag('actor_files', [file,animation,coll]) 
    else:
        try:
            model.find('**/collision').setCollideMask(BitMask32.bit(2))        
            model.find('**/collision').setPythonTag('object', model)        
        except:
            print "WARNING: Model {0} has no collision geometry!\nGenerating collision sphere...".format(file)
            bounds=model.getBounds()
            radi=bounds.getRadius()
            cent=bounds.getCenter()
            coll_sphere=model.attachNewNode(CollisionNode('collision'))
            coll_sphere.node().addSolid(CollisionSphere(cent[0],cent[1],cent[2], radi)) 
            coll_sphere.setCollideMask(BitMask32.bit(2))        
            coll_sphere.setPythonTag('object', model)
            #coll_sphere.show()
            if animation:
                model.setPythonTag('actor_files', [file,animation,None])
    return model    
        
def LoadScene(file, quad_tree, actors, terrain, textures, current_textures=None, flatten=False):
    json_data=None
    with open(file) as f:  
        json_data=json.load(f)
    return_data=[]    
    for object in json_data:
        print ".",
        model=None
        if 'textures' in object:
            i=0
            for tex in object['textures']:
                if tex in textures:
                    if current_textures:
                        id=textures.index(tex)                    
                        current_textures[i]=id
                    terrain.setTexture(terrain.findTextureStage('tex{0}'.format(i+1)), loader.loadTexture(tex), 1)
                    #normal texture should have the same name but should be in '/normal/' directory
                    normal_tex=tex.replace('/diffuse/','/normal/')
                    terrain.setTexture(terrain.findTextureStage('tex{0}n'.format(i+1)), loader.loadTexture(normal_tex), 1)
                else:
                    print "WARNING: texture '{0}' not found!".format(tex)
                i+=1
            continue    
        elif 'model' in object:
            model=loadModel(object['model'])            
        elif 'actor' in object:
            model=loadModel(object['actor'],object['actor_collision'],object['actor_anims'])
            actors.append(model)
        else:
            return_data.append(object)
        if model:    
            model.reparentTo(quad_tree[object['parent_index']])        
            model.setPythonTag('props', object['props'])
            model.setHpr(render,object['rotation_h'],object['rotation_p'],object['rotation_r'])
            model.setPos(render,object['position_x'],object['position_y'],object['position_z'])
            model.setScale(object['scale'])
    
    if flatten:
        for node in quad_tree:
            flat=render.attachNewNode('flatten')
            for child in node.getChildren():
                if child.getPythonTag('props')=='': #objects with SOME properties should be keept alone
                    child.clearPythonTag('model_file')
                    child.clearPythonTag('props')
                    child.clearModelNodes()
                    child.wrtReparentTo(flat)
            flat.flattenStrong()
            flat.wrtReparentTo(node)            
    return return_data
    
def SaveScene(file, quad_tree, textures, current_textures=None, extra_data=None):
    export_data=[]
    if extra_data:
        export_data.append(extra_data)
    if current_textures:
        temp=[]
        for id in current_textures:
            temp.append(textures[id])    
        export_data.append({'textures':temp})    
    else:
        export_data.append({'textures':textures})
    for node in quad_tree:
        for child in node.getChildren():
            temp={}
            if child.hasPythonTag('model_file'):
                temp['model']=unicode(child.getPythonTag('model_file'))
            elif child.hasPythonTag('actor_files'):
                temp['actor']=unicode(child.getPythonTag('actor_files')[0])
                temp['actor_anims']=child.getPythonTag('actor_files')[1]
                temp['actor_collision']=child.getPythonTag('actor_files')[2]
            temp['rotation_h']=child.getH(render)
            temp['rotation_p']=child.getP(render)
            temp['rotation_r']=child.getR(render)            
            temp['position_x']=child.getX(render)
            temp['position_y']=child.getY(render)
            temp['position_z']=child.getZ(render)
            temp['scale']=child.getScale()[0]            
            temp['parent_name']=node.getName()
            temp['parent_index']=quad_tree.index(node)
            temp['props']=unicode(child.getPythonTag('props'))
            export_data.append(temp)
    with open(file, 'w') as outfile:
        json.dump(export_data, outfile, indent=4, separators=(',', ': '), sort_keys=True)        