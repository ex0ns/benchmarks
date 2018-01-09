#!/usr/bin/python
import os
import errno
import subprocess as subp

def where(cmd):
    if os.path.isfile(cmd):
        return cmd
    else:
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            f = os.path.join(p, cmd)
            if os.path.isfile(f):
                return f
        else:
            return None

def run(cmd):
    print(">>> " + str(cmd))
    process = subp.Popen(cmd)
    result = process.communicate()
    if process.returncode != 0:
        print '>>> non-zero return code ' + str(process.returncode)
    return process.returncode == 0

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def link(bench, conf):
    sbt = where('sbt')
    command = ['sbt', '-mem', '8096', 'clean']
    command.append('set nativeBenchmark := "{}"'.format(bench))
    command.extend(settings(conf))
    command.append('nativeLink')
    return run(command)

def settings(conf):
    out = []
    for key, value in conf.iteritems():
        if key == 'name':
            pass
        elif key == 'native':
            with open('project/plugins.sbt', 'w') as f:
                f.write('addSbtPlugin("org.scala-native" % "sbt-scala-native" % "{}")'.format(value))
        elif key == 'clang':
            clang = where('clang{}'.format(value))
            clangpp = where('clang++{}'.format(value))
            out.append('set nativeClang := file("{}")'.format(clang))
            out.append('set nativeClangPP := file("{}")'.format(clangpp))
        elif key == 'scala':
            out.append('set scalaVersion := "{}"'.format(value))
        elif key == 'mode':
            out.append('set nativeMode := "{}"'.format(value))
        elif key == 'gc':
            out.append('set nativeGC := "{}"'.format(value))
        elif key == 'llvm':
            out.append('set disableLLVM := "{}"'.format(value))
        elif key == 'depth':
            out.append('set inliningDepth := {}'.format(value))
        elif key == 'methodSize':
            out.append('set maxMethodSize := {}'.format(value))
        elif key == 'inliningThreshold':
            out.append('set inliningThreshold := {}'.format(value))
        elif key == 'disableLLVM':
            out.append('set disableLLVM := {}'.format(value))
        elif key == 'disableEscape':
            out.append('set disableEscape := {}'.format(value))
        else:
            raise Exception('Unkown configuration key: ' + key)
    return out

def conf(**kwargs):
    return kwargs

configurations = [ ]
gc = 'immix'
disableLLVM = 'true'
disableEscape = 'true'
depth = 2
maxMethodSize = 2048
inliningThreshold = 110
configurations.append(conf(name='GC-{}_DisableLLVM-{}_DisableEscape-{}_Depth-{}_MethodSize-{}_InliningThreshold-{}'.format(gc, disableLLVM, disableEscape, depth, maxMethodSize, inliningThreshold), native='0.4.0-SNAPSHOT', clang='', scala='2.11.11', mode='release', gc=gc, depth=depth, methodSize=maxMethodSize, inliningThreshold=inliningThreshold, disableLLVM=disableLLVM, disableEscape=disableEscape))

#for gc in ['immix']:
#    for disableLLVM in ['true', 'false']:
#        for disableEscape in ['true', 'false']:
#            for depth in [2, 4, 8, 16]:
#                for maxMethodSize in [2048, 4096, 16384, 32768]:
#                    for inliningThreshold in [16, 32, 64, 128]:
#                        configurations.append(conf(name='GC-{}_DisableLLVM-{}_DisableEscape-{}_Depth-{}_MethodSize-{}_InliningThreshold-{}'.format(gc, disableLLVM, disableEscape, depth, maxMethodSize, inliningThreshold), native='0.4.0-SNAPSHOT', clang='', scala='2.11.11', mode='release', gc=gc, depth=depth, methodSize=maxMethodSize, inliningThreshold=inliningThreshold, disableLLVM=disableLLVM, disableEscape=disableEscape))

benchmarks = [
        'bounce'
        #'brainfuck',
        #'json',
#        'kmeans',
#        'list',
#        'nbody',
#        'permute',
        #'queens',
#        'richards',
        #'sudoku'
#        'tracer'
]

runs = 10

iterations = 1000

if __name__ == "__main__":
    for bench in benchmarks:
        for conf in configurations:
            mkdir('results/{}/{}/'.format(bench, conf['name']))
            link(bench, conf)
            for runid in xrange(runs):
                outfile = 'results/{}/{}/{}.data'.format(bench, conf['name'], runid)
                run(['target/scala-2.11/benchmarks-out', str(iterations), outfile])
