// Wrappers
var _STANDARD_MAT = THREE.MeshLambertMaterial
var random = Math.random;
var max = Math.max;
var floor = Math.floor;

// Numbers/hex/etc.
var RED = 0xff0000;
var GREEN = 0x00ff00;
var BLUE = 0x0000ff;
var WHITE = 0xffffff;

// Materials
var DEFAULT_MAT = new _STANDARD_MAT({color: 0xffffff});
var ACTIVE_MAT = new _STANDARD_MAT({color: GREEN, ambient: GREEN});
var INACTIVE_MAT = new _STANDARD_MAT({color: RED, ambient: RED});

// Meshes
var UNIT_CUBE = new THREE.CubeGeometry(1., 1., 1.);

// Misc. Constants
var ORIGIN = new THREE.Vector3(0,0,0);

// Helper Functions
var makeMesh = function (object){
  return new THREE.Mesh(object.geometry, object.material);
}
