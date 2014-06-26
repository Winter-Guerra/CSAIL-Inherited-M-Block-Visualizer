// Test 1 -- proof of concept
var Test = function() {
  var that = this;
  this.scene = new THREE.Scene();
  this.pivot = new THREE.Object3D();
  this.pivot.rotation.x -= 1.57079632679;
  this.scene.add(this.pivot);
  this.camera = new THREE.PerspectiveCamera(
      75,window.innerWidth/window.innerHeight, 0.1, 1000);

  this.renderer = new THREE.WebGLRenderer();
  this.renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(this.renderer.domElement);

  // FORNOW: Helper function to maintain consistency
  this.addCube = function(cube) {
    that.pivot.add(cube);
    that.cubes[that.cubes.length] = cube;
  }


  this.setupScene = function() {
    // data structures
    that.cubes = new Array();
    // TODO EXPERIMENTAL: grid
    var size = 10;
    var step = 1;
    var gridHelper = new THREE.GridHelper(15, 1 );
    gridHelper.position = new THREE.Vector3(.5, .5, -.5);
    gridHelper.rotation = new THREE.Euler(-1.57079632679, 0, 0);
    gridHelper.setColors('white', 'grey');
    that.pivot.add(gridHelper);
    

    // keyboard
    this.keyboard = new THREEx.KeyboardState();

    // // camera/lights
    that.camera.position.y = 2.;
    that.camera.position.z = 5.;
    that.camera.lookAt(ORIGIN);
    // ambient and directional lights
    var ambientLight = new THREE.AmbientLight(0x333333);
    var directionalLight = new THREE.DirectionalLight(0xffffff);
    directionalLight.position.set(1, 1, 1).normalize();
    that.scene.add(ambientLight);
    that.scene.add(directionalLight);

    // cubes
    for (var i = 0; i < 5; i++) {
      var cube = makeMesh({geometry: UNIT_CUBE, material: DEFAULT_MAT});
      // clamp the cube to Z3, z>=0
      cube.position = new THREE.Vector3(
          floor(i*(-.5+random())),
          floor(i*(-.5+random())),
          max(0,floor(i*(-.5+random()))));
      that.addCube(cube);
    }
  }

  this.update = function() {

    // // keyboard handling
    // rotation
    if (that.keyboard.pressed('d') && !that.dHeld) {
      that.dHeld = true;
      if (!that.rotateL)
        that.rotateR = !that.rotateR;
      else
        that.rotateR = false;
      that.rotateL = false;
    } else if (!that.keyboard.pressed('d')) {
      that.dHeld = false;
    }

    if (that.keyboard.pressed('a') && !that.aHeld) {
      that.aHeld = true;
      if (!that.rotateR)
        that.rotateL = !that.rotateL;
      else
        that.rotateL = false;
      that.rotateR = false;
    } else if (!that.keyboard.pressed('a')) {
      that.aHeld = false;
    }

    // stepping
    if (that.keyboard.pressed('s') && !that.sHeld) {
      that.sHeld = true;
      that.doStep = true;
    } else if (!that.keyboard.pressed('s')) {
      that.sHeld = false;
      that.doStep = false;
    } else {
      that.doStep = false;
    }

    // // TODO: reset
    // if (that.keyboard.pressed('r'))
      // that.setupScene();

    // assign colors
    // perform moves
    if (that.doStep) {
      // TODO: Strip into pick current cube function
      var curr_cube_i = floor(random()*that.cubes.length);
      for (var i = 0; i < that.cubes.length; i++) {
        if (i == curr_cube_i) {
          that.cubes[i].material = ACTIVE_MAT;
          function sign(x) {
              return typeof x === 'number' ?
                x ? x < 0 ? -1 : 1 : x === x ? 0 : NaN : NaN;
          }
          // TODO: Strip into move function
          that.cubes[i].position.x += sign(-.5+random());
          that.cubes[i].position.y += sign(-.5+random());
          // that.cubes[i].position.z += max(0,sign(-.5+random()));
        } else {
          that.cubes[i].material = INACTIVE_MAT;
        }
      }
    }
  }

  this.render = function() {
    // update call
    that.update()

    requestAnimationFrame(that.render);
    if (that.rotateR)
      that.pivot.rotation.z += .015;
    else if (that.rotateL)
      that.pivot.rotation.z += -.015;
    that.renderer.render(that.scene, that.camera);
  }
}
