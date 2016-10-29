import sys

def bf(project, code=None, threshold=3):
    Backfill(project, threshold=threshold, code=code).RTdict()
    return

class Backfill():
    def __init__(self, project, threshold=3, code=None):
        self._project = project
        self._threshold = threshold
        self._code = code

    def RTdict(self):
        if not self._code:
            for code in self._project.lib.library:
                self.check_code(code)
        else:
            self.check_code(self._code)
        return

    def check_code(self, code):
        if self.enough(code):
            self.bf(code)
        return

    def enough(self, code):
        count = 0
        for sample in self._project.runlist:
            if code in self._project.RTdict[sample]:
                count += 1
        if count >= self._threshold:
            return True
        else:
            return False
            
    def bf(self, code):
        for sample in self._project.runlist:
            print(self._project.RTdict[sample][code])
            if not self._project.RTdict[sample][code]:
                print('get new RT')
                RT_lib = self._project.lib.RT(code)
                CF = self._project.CFdict[sample]
                self._project._RTdict[sample][code] = \
                ((RT_lib - CF[1]) / CF[0], 0)
        return



                


def bf_old(RTdict, CFdict, library, threshold=3):
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
            
