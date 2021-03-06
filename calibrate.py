import os, sys, library, amdis, warnings
import project as proj
import statistics as stat
import numpy as np
import matplotlib.pyplot as plt

class SaveImage():
    def __init__(self, align_dir, sample_y):
        self._dir = align_dir
        self._sample_y = sample_y
        
    def save_image(self, x, y, CF, sample_x):
        x_line = np.arange(0.,max(x))
        y_line = x_line*CF[0]+CF[1]
        x = np.array(x)
        y = np.array(y)
        plt.figure()
        plt.scatter(x,y)
        plt.plot(x_line, y_line, 'r-')
        plt.xlabel(self._sample_y)
        plt.ylabel(sample_x)
        plot_name = os.path.join(self._dir,'{0}.png'.format(sample_x))
        plt.savefig(plot_name)
        plt.close()
        return

#---End of Class SaveImage-------------------------------------------


class Align(object):
    def __init__(self, project, RT_dict, library):
        self._project = project
        self._RT = RT_dict
        self._library = library
        self._slope = project.info.slope
        self._lim = project.info.lim
        self._ref = project.info.sample_ref-1
        ref_name = self._project.runlist[self._ref]
        self._image = SaveImage(self._project.path.align_dir,
                sample_y = ref_name) 

    def align(self):
        CF = {}
        self._ref_name = self._project.runlist[self._ref]
        CF[self._ref_name] = (1.,0.)
        for sample in self._project.runlist:
            if not sample == self._ref_name:
                print('\t{0} vs {1}\t\t\r'.format(self._ref_name, sample),)
                CF[sample] = self.align_sample(sample)
        print('Align against reference library')
        CF = self.align_ref(CF)
        return CF

    def align_sample(self, sample):
        x=[]
        y=[]
        for code in self._RT[self._ref_name]:
            if code in self._RT[sample]: 
                x.append(self._RT[sample][code][0])
                y.append(self._RT[self._ref_name][code][0])
        CF = stat.reg_robust(x,y,slope=self._slope, lim=self._lim)
        self._image.save_image(x,y,CF,sample_x=sample)
        return CF

    def align_ref(self, CF_RT):
        lib_file = self._project.path.library_file_ref
        code_set = get_code_set(self._RT)
        x = []
        y = []
        RT_ref = {}
        for sample in self._RT:
            CF = CF_RT[sample]
        for code in self._RT[sample]:
            RT_ref.setdefault(code, []).append\
                              (self._RT[sample][code][0]*CF[0]+CF[1])
        for code in self._library.library:
            if code in RT_ref:
                x.append(stat.median(RT_ref[code]))
                y.append(self._library.library[code]['RT'])
        CF_ref = stat.reg_robust(x,y,slope=self._slope, lim=self._lim)
        self._image.save_image(x,y,CF_ref,sample_x='Reference')
        CF_new = {}
        for sample in self._project.runlist:
            CF_new[sample] = (CF_RT[sample][0]*CF_ref[0], 
                                CF_RT[sample][1]*CF_ref[0]+CF_ref[1])
        return CF_new

#---end of class Align-----------------------------------------------------

class Calibrate(object):
    def __init__(self, project):
        self._project = project
        self._csv = project.csv
        self._runlist = project.runlist
        self._cal_file = project.path.runlist_file
        self._library = library.Library(project.path.library_file_ref, 
                                        project.csv)

    def calibrate(self):
        self.setup_data()
        print('Align samples')
        self.align_samples()
        print('Create library')
        self.create_library()
        self.save_files()
        return

    def setup_data(self):
        move_amdis(self._project.path)
        self.get_RT()
        self.remove_ignore()
        return

    def align_samples(self):
        align = Align(self._project, self._RTdict, self._library)
        self._CF = align.align()
        self.save_cal_file()
        return

    def save_cal_file(self):
        with open(self._project.path.runlist_file_cal, 'r') as runlist:
            lines = runlist.readlines()
        with open(self._project.path.runlist_file, 'w') as callist:
            for line in lines:
                info = self._csv.read_line(line)
                CF = self._CF[info[0].lower()]
                line_list = info + [CF[0] , CF[1]]
                callist.write(self._csv.make_line(line_list))
        return

    def datadict(self):
        self._datadict = {}
        for sample in self._CF:
            amdis_file = self._project.path.amdis_file_sample(sample)
            amdis_sample = amdis.Sample(amdis_file, library=self._library, 
                                        CF=self._CF[sample]) 
            self._datadict[sample] = amdis_sample.data()
        return

    def codedict(self):
        self._codedict = {}
        for sample in self._datadict:
            CF = self._CF[sample]
            for code in self._datadict[sample]:
                RT_ref = self._datadict[sample][code][0]*CF[0] + CF[1]
                self._codedict.setdefault(code, []).append(RT_ref)
        return 

    def create_library(self):
        self._library = library.Library(self._project.path.library_file_ref,
                                        self._project.csv)
        self.datadict()
        self.codedict()
        refineRT = False
        if self._project.info.auto_RT == 'yes':
            refineRT = True
            factor = self._project.info.refine_factor
        for code in list(self._library.library.keys()):
            if not code in self._codedict:
                del self._library.library[code]
            elif refineRT == True:
                self._library.library[code]['RT'] = \
                              stat.median(self._codedict[code])
                self._library.library[code]['lim'] /= factor
        self._codelist = self._library.write_library\
                             (self._project.path.library_file)
        return

    def refineRT(self):
        factor = self._project.info.refine_factor
        for code in self._library.library:
            self._library.library[code]['RT'] = stat.median(code_dict[code])
            self._library.library[code]['lim'] /= factor
        return

    def save_files(self):
        writedata = WriteData(self)
        writedata.savefile()
        return

    def get_RT(self):
        self._RTdict = {}
        for sample in self._runlist:
            path = self._project.path.amdis_file_sample(sample)
            amdis_sample = amdis.Sample(path, library= self._library)
            self._RTdict[sample] = amdis_sample.data(cal=True)
        return

    def remove_ignore(self):
        for sample in self._RTdict:
            try:
                for code in self._project.info.codes_ignore:
                    del self._RTdict[sample][code]
            except:
                pass
        return

#---End of Class Calibration--------------------------------------
class WriteData(object):
    def __init__(self, calibrate):
        self._project = calibrate._project
        self._RTdict = calibrate._datadict
        self._codelist = calibrate._codelist
        self._CFdict = calibrate._CF

    def savefile(self):
        RT_file = self._project.path.align_data_file
        with open(RT_file, 'w') as data:
            data.write(self.header())
            for code in self._codelist:
                data.write(self.line(code))
        return

    def line(self, code):
        info = [code]
        for sample in self._project.runlist:
            CF = self._CFdict[sample]
            try:
                data = list(self._RTdict[sample][code])
                RT_ref = data[0]*CF[0]+CF[1]
                data.insert(1, RT_ref)
            except KeyError:
                data = ["","",""]
            info.extend(data)
        return self._project.csv.make_line(info)

    def header(self):
        info1 = ['sample']
        info2 = ['code']
        for sample in self._project.runlist:
            info1.extend([sample, "", ""])
            info2.extend(['RT','RT_ref','fit'])
        line1 = self._project.csv.make_line(info1)
        line2 = self._project.csv.make_line(info2)
        return line1 + line2

#---End of Class WriteData----------------------------------


def linreg(x,y,slope):
    linfit = statistics.LinFit(x,y,slope=slope)
    return linfit.lin_fit()


def get_code_set(RT_dict):
    code_set = set()
    for sample in RT_dict:
        for code in RT_dict[sample]:
            code_set.add(code)
    return code_set

def move_amdis(path):
    amdis_file = path.amdis_file
    if amdis_file:
        amdis.batch(path)
        os.unlink(path.amdis_file)
    return

def create_dir(path):
    if not os.path.exists(path._project_dir):
        os.mkdir(path._project_dir)
    if not os.path.exists(path.amdis_dir):
        os.mkdir(path.amdis_dir)
    if not os.path.exists(path.align_dir):
        os.mkdir(path.align_dir)
    return

def main(project_name = None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    project = proj.Project(project_name)
    project.prepare_calibrate()
    warnings.simplefilter("error", FutureWarning)
    Calibrate(project).calibrate()
    print('\a')
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
