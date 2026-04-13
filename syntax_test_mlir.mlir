// SYNTAX TEST "Packages/mlir-toc/mlir.sublime-syntax"

  affine.for
//^^^^^^^^^^ entity.name.function.affine.mlir

  affine_map
//^^^^^^^^^^ entity.name.function.affine.structure.mlir

  llvm.add
//^^^^^^^^ entity.name.function.llvm.integer.mlir

  llvm.return
//^^^^^^^^^^ keyword.return.llvm.mlir

  llvm.func
//^^^^^ keyword.function.llvm.mlir

  gpu.module
//^^^^^^^^^^ keyword.other.gpu.module.mlir

  gpu.barrier
//^^^^^^^^^^^ entity.name.function.gpu.mlir

  vector.broadcast
//^^^^^^^^^^^^^^^^ entity.name.function.vector.mlir

  loop.for
//^^^^^^^^ entity.name.function.loop.mlir

  nvvm.barrier0
//^^^^^^^^^^^^^ entity.name.function.nvvm.barrier.mlir

  "tfl.abs"
//^^^^^^^^^ entity.name.function.tensorflow_lite.mlir

  "affine.for"
//^^^^^^^^^^^^ entity.name.function.affine.mlir

%ssa
//<- variable.parameter.mlir

  ^bb1
//^^^^ entity.name.label.mlir

  func @myfunc
//^^^^ keyword.function.mlir
//     ^^^^^^^ entity.name.function.mlir

  i32
//^^^ storage.type.mlir

  return
//^^^^^^ keyword.module.mlir

  memref<i32>
//       ^^^ storage.type.size.mlir

  "x"
// ^ string.quoted.double.mlir

  "bad\z"
//    ^^ invalid.illegal.string.mlir

  // plain comment
//^^^^^^^^^^^^^^^^ comment.line.double-slash.mlir

  // CHECK: i32
//^^^^^^^^^^^^^ comment.line.double-slash.mlir
//   ^^^^^^ comment.other.filecheck.mlir
//          ^^^ storage.type.mlir
