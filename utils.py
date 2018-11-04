import os, sys


    
def write_html(path, html):
        
    pathDir = path.split('/')

    name = pathDir[-1]
    pathDir.pop()[-1]

    createPath = ""
    
    for fold in pathDir:
        createPath += fold + "/"
        if not os.path.exists(createPath):
            os.mkdir(createPath)


    if (os.path.exists(createPath + name)):
        os.remove(createPath + name)
    if isinstance(html, str):
        with open(createPath + name, '+w') as file:
            file.write(html)
    else:
        with open(createPath + name, "wb") as file:
            try:
                file.write(html)
            except:
                print("Error while writing ", html, "in", createPath + name)


def path_exists(path):
    return(os.path.exists(path))
