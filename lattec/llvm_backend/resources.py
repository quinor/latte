LLVM_RUNTIME = """
@dnl = internal constant [4 x i8] c"%d\\0A\\00"
@fnl = internal constant [6 x i8] c"%.1f\\0A\\00"
@d   = internal constant [3 x i8] c"%d\\00"
@lf  = internal constant [4 x i8] c"%lf\\00"

declare i32 @printf(i8*, ...)
declare i32 @scanf(i8*, ...)
declare i32 @puts(i8*)
declare noalias i8* @malloc(i32)
declare void @free(i8*)
declare i32 @strlen(i8*)
declare i8* @strcpy(i8*, i8*)
declare i32 @strcmp(i8*, i8*)

%struct.S = type { i8*, i32 }

define void @printInt(i32 %x) {
       %t0 = getelementptr [4 x i8], [4 x i8]* @dnl, i32 0, i32 0
       call i32 (i8*, ...) @printf(i8* %t0, i32 %x)
       ret void
}

define i32 @readInt() {
entry:  %res = alloca i32
        %t1 = getelementptr [3 x i8], [3 x i8]* @d, i32 0, i32 0
    call i32 (i8*, ...) @scanf(i8* %t1, i32* %res)
    %t2 = load i32, i32* %res
    ret i32 %t2
}


; string functions


define dso_local noalias %struct.S* @__builtin__add_string(%struct.S* nocapture readonly, %struct.S* nocapture readonly) local_unnamed_addr {
  %3 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 0
  %4 = load i8*, i8** %3
  %5 = tail call i32 @strlen(i8* %4)
  %6 = getelementptr inbounds %struct.S, %struct.S* %1, i32 0, i32 0
  %7 = load i8*, i8** %6
  %8 = tail call i32 @strlen(i8* %7)
  %9 = add i32 %5, 1
  %10 = add i32 %9, %8
  %11 = tail call noalias i8* @malloc(i32 %10)
  %12 = tail call noalias i8* @malloc(i32 8)
  %13 = bitcast i8* %12 to %struct.S*
  %14 = tail call i8* @strcpy(i8* %11, i8* %4)
  %15 = getelementptr inbounds i8, i8* %11, i32 %5
  %16 = load i8*, i8** %6
  %17 = tail call i8* @strcpy(i8* %15, i8* %16)
  %18 = getelementptr inbounds i8, i8* %12, i32 4
  %19 = bitcast i8* %18 to i32*
  store i32 1, i32* %19
  %20 = bitcast i8* %12 to i8**
  store i8* %11, i8** %20
  ret %struct.S* %13
}

define dso_local i32 @__builtin__eq_string(%struct.S* nocapture readonly, %struct.S* nocapture readonly) local_unnamed_addr {
  %3 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 0
  %4 = load i8*, i8** %3
  %5 = getelementptr inbounds %struct.S, %struct.S* %1, i32 0, i32 0
  %6 = load i8*, i8** %5
  %7 = tail call i32 @strcmp(i8* %4, i8* %6)
  %8 = icmp eq i32 %7, 0
  %9 = zext i1 %8 to i32
  ret i32 %9
}

define dso_local i32 @__builtin__ne_string(%struct.S* nocapture readonly, %struct.S* nocapture readonly) local_unnamed_addr {
  %3 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 0
  %4 = load i8*, i8** %3
  %5 = getelementptr inbounds %struct.S, %struct.S* %1, i32 0, i32 0
  %6 = load i8*, i8** %5
  %7 = tail call i32 @strcmp(i8* %4, i8* %6)
  %8 = icmp ne i32 %7, 0
  %9 = zext i1 %8 to i32
  ret i32 %9
}

define dso_local void @__builtin__destroy_string(%struct.S* nocapture) local_unnamed_addr {
  %2 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 1
  %3 = load i32, i32* %2
  %4 = add i32 %3, -1
  store i32 %4, i32* %2
  %5 = icmp eq i32 %4, 0
  br i1 %5, label %6, label %10

; <label>:6:                                      ; preds = %1
  %7 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 0
  %8 = load i8*, i8** %7
  tail call void @free(i8* %8)
  %9 = bitcast %struct.S* %0 to i8*
  tail call void @free(i8* %9)
  br label %10

; <label>:10:                                     ; preds = %6, %1
  ret void
}

define dso_local void @printString(%struct.S* nocapture readonly) local_unnamed_addr {
  %2 = getelementptr inbounds %struct.S, %struct.S* %0, i32 0, i32 0
  %3 = load i8*, i8** %2
  %4 = tail call i32 @puts(i8* %3)
  ret void
}


"""


def string_constant(name: str, value: str) -> str:
    vl = len(value)+1
    return (
        f"@_{name} = internal constant [{vl} x i8] c\"{value}\\00\"\n"
        f"@{name} = global %struct.S {'{'} i8* getelementptr inbounds ([{vl} x i8], [{vl} x i8]* @.str, i32 0, i32 0), i32 1000000000 {'}'}\n"
    )
