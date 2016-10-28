import sys

def bf(project, threshold=3):
    Backfill(project, threshold).RTdict
    return

class Backfill():
    def __init__(self, project, threshold=3):
        self._lib = project.lib
        self._CFdict = project.CFdict
        self._RTdict = project.RTdict

    def RTdict(self):
        for code in self.lib:
            if enough:
                self.bf(code)
                #update RTdict and Cfdict in project
        return

    def enough(self, code):
        count = 0
        for sample in self._project.runlist:
            if code in RTDict[sample]:
                count += 1
        if count >= self._threshold:
            return True
        else:
            return False
            
    def bf(self, code):
        for sample in self._project.runlist:
            if not self._RTdict[sample][code]:
                #calc RT
                #updat RT and fit in project class


                

def bf(project):
    RTlist =  make_RTlist(project)
    for code in Rtlist:
        RT_lib = project.library.RT(code)
        for sample in RTDict

def bf(RTdict, CFdict, library, threshold=3):
    RTlist = make_RTlist (RTdict, threshold)
    print(RTlist)
    sys.exit(2)
    for code in RTlist:
        RT_lib = library.RT(code)
        for sample in RTdict:
            CF = CFdict[sample]
            if not code in sample:
                RTdict[sample][code] = ((RT_lib - CF[1]) / CF[0], 0)
    return RTdict

def make_RTlist(RTdict, threshold):
    RT_count = {}
    RT_list = []
    for sample in RTdict:
        for code in RTdict[sample]:
            RT_count[code] = RT_count.setdefault(code, 0) + 1
    for i in RT_count:
        if threshold < RT_count[i] <len(RTdict):
            RT_list.append(i)
    return RT_list
            
