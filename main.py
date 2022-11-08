# Display a scene in VR
from TLE.TLEParsing import *
import harfang as hg
import sys

hg.InputInit()
hg.WindowSystemInit()

res_x, res_y = 1280, 720
win = hg.RenderInit("Harfang - OpenVR Scene", res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

hg.AddAssetsFolder("assets_compiled")

pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

render_data = hg.SceneForwardPipelineRenderData()  # this object is used by the low-level scene rendering API to share view-independent data with both eyes

flag_vr = False

# OpenVR initialization
if flag_vr:
    if not hg.OpenVRInit():
        sys.exit()

    vr_left_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)
    vr_right_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)

# Create models
vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

cube_mdl = hg.CreateCubeModel(vtx_layout, 1, 1, 1)
cube_ref = res.AddModel('cube', cube_mdl)
earth_model_radius = 1
sphere_mdl = hg.CreateSphereModel(vtx_layout, earth_model_radius, 64, 64)
sphere_ref = res.AddModel('sphere', sphere_mdl)

ground_mdl = hg.CreateCubeModel(vtx_layout, 5, 0.01, 5)
ground_ref = res.AddModel('ground', ground_mdl)

# Load shader
prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

# Create materials
def create_material(ubc, orm, slf, blend_mode= hg.BM_Opaque):
    mat = hg.Material()
    hg.SetMaterialProgram(mat, prg_ref)
    hg.SetMaterialValue(mat, "uBaseOpacityColor", ubc)
    hg.SetMaterialValue(mat, "uSelfColor", slf)
    hg.SetMaterialValue(mat, "uOcclusionRoughnessMetalnessColor", orm)
    hg.SetMaterialBlendMode(mat, blend_mode)
    return mat

# Create scene
scene = hg.Scene()
scene.canvas.color = hg.ColorI(0, 0, 0, 255)
scene.environment.ambient = hg.ColorI(2, 2, 4, 255)

cam_pos = hg.Vec3(-1.3, .45, -2)
cam_rot = hg.Deg3(0, 0, 0)
cam_mtx = hg.TransformationMat4(cam_pos, cam_rot)
cam = hg.CreateCamera(scene, cam_mtx, 0.01, 5000)
scene.SetCurrentCamera(cam)

lgt = hg.CreateSpotLight(scene, hg.TransformationMat4(hg.Vec3(-8, 4, -5), hg.Vec3(hg.Deg(19), hg.Deg(59), 0)), 0, hg.Deg(5), hg.Deg(30), hg.Color.White, hg.Color.White, 10, hg.LST_None, 0.0001)
#back_lgt = hg.CreatePointLight(scene, hg.TranslationMat4(hg.Vec3(2.4, 1, 0.5)), 10, hg.Color(94 / 255, 255 / 255, 228 / 255, 1), hg.Color(94 / 255, 1, 228 / 255, 1), 0)

mat_cube = create_material(hg.Vec4(255 / 255, 230 / 255, 20 / 255, 1), hg.Vec4(1, 0.658, 0., 1), hg.Vec4(1, 1, 0, 1))


mat_sphere = create_material(hg.Vec4(16 / 255, 32 / 255, 255 / 255, 0.5), hg.Vec4(1, 0.658, 0., 1), hg.Vec4(0, 0, 0, 0))
hg.CreateObject(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(0, 0, 0)), sphere_ref, [mat_sphere])

mat_ground = create_material(hg.Vec4(0, 0, 0, 0.5), hg.Vec4(1, 1, 0.1, 1), hg.Vec4(0.1, 0.1, 0.1, 1), hg.BM_Alpha)
hg.CreateObject(scene, hg.TranslationMat4(hg.Vec3(0, -2, 0)), ground_ref, [mat_ground])

keyboard = hg.Keyboard()
mouse = hg.Mouse()

# Extract orbit

#Open TLE file
file = open('TLE/TLE 100 or so brightest 2022 Oct 24 12_05_27 UTC.txt', 'r')
Lines = file.readlines()

#Ignore name line and grab 2 next lines
i=0
objects = []
while i < len(Lines):
    objects.append({"orbit": Lines[i+1] + Lines[i+2], "plot": hg.CreateObject(scene, hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(0, 0, 0), hg.Vec3(0.01, 0.01, 0.01)), cube_ref, [mat_cube])})
    i+=3

t_orbit = 0

# Main loop
while not hg.ReadKeyboard().Key(hg.K_Escape) and hg.IsWindowOpen(win):
    dt = hg.TickClock()
    keyboard.Update()
    mouse.Update()

    hg.FpsController(keyboard, mouse, cam_pos, cam_rot, 20 if keyboard.Down(hg.K_LShift) else 8, dt)

    cam.GetTransform().SetPos(cam_pos)
    cam.GetTransform().SetRot(cam_rot)

    #Get orbit position:
    earth_radius = 6370000
    scale = earth_model_radius / earth_radius
    t_orbit += hg.time_to_sec_f(dt) * 1000
    for object in objects:
        x,y,z = propagTLEinXYZ(object["orbit"], t_orbit)
        pos = hg.Vec3(x, y, z) * scale
        object["plot"].GetTransform().SetPos(pos)

    scene.Update(dt)

    vid = 0  # keep track of the next free view id
    passId = hg.SceneForwardPipelinePassViewId()

    # Prepare view-independent render data once
    vid, passId = hg.PrepareSceneForwardPipelineCommonRenderData(vid, scene, render_data, pipeline, res, passId)

    if flag_vr :
        actor_body_mtx = hg.TransformationMat4(cam_pos, hg.Vec3(0, 0, 0))

        vr_state = hg.OpenVRGetState(actor_body_mtx, 0.01, 1000)
        left, right = hg.OpenVRStateToViewState(vr_state)
        vr_eye_rect = hg.IntRect(0, 0, vr_state.width, vr_state.height)

        # Prepare the left eye render data then draw to its framebuffer
        vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, left, scene, render_data, pipeline, res, passId)
        vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, left, pipeline, render_data, res, vr_left_fb.GetHandle())

        # Prepare the right eye render data then draw to its framebuffer
        vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, right, scene, render_data, pipeline, res, passId)
        vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, right, pipeline, render_data, res, vr_right_fb.GetHandle())

    # Main screen
    view_state = scene.ComputeCurrentCameraViewState(hg.ComputeAspectRatioX(res_x, res_y))
    vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, view_state, scene, render_data, pipeline, res, passId)
    vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, hg.IntRect(0, 0, res_x, res_y), view_state, pipeline, render_data, res)

    hg.Frame()
    if flag_vr:
        hg.OpenVRSubmitFrame(vr_left_fb, vr_right_fb)

    hg.UpdateWindow(win)

hg.DestroyForwardPipeline(pipeline)
hg.RenderShutdown()
hg.DestroyWindow(win)
