import datafiles, mzratio, CDF, sys, normfiles, normfigures, baseline
import project as proj

class Data(object):
    def __init__(self, project, normalize):
        project.read_library()
        self._project = project
        self._normalize = normalize
        self.cdf()
        self._datadict = datafiles.data(project.path.hdf5)

    def import_data(self):
        with datafiles.HDF5(project.path.hdf5):
            RTdict = datafiles.RTdict()
            areadict = datafiles.areadict()


    def import_data_old(self):
        self.cdf()
        self._datadict = {}
        for sample in self._project.runlist:
            data = datafiles.DataFiles(self._project, sample).read_file()
            self._datadict[sample] = data
        self.get_area_TIC()
        self.norm_area()
        return

    def cdf(self):
        self._baseline = {}
        self._TIC = {}
        self._time = {}
        self._emptyTIC = {}
        for sample in self._project.runlist:
            cdf = CDF.CDF(sample)
            self._emptyTIC[sample] = cdf.empty_TIC
            self._time[sample] = cdf.scan_time
            self._TIC[sample] = cdf.total_TIC
            self._baseline[sample] = baseline.baseline_poly\
                                     (self._time[sample], self._TIC[sample],
                                      window=50, deg=10)
        return

    def get_area_TIC(self):
        for code in self._project._library._lib:
            CF = self._normalize.CF(code)
            for sample in self._project.runlist:
                try:
                    self._datadict[sample][code]['area'] *= CF
                except KeyError:
                    pass
                try:
                    self._datadict[sample][code]['param'][0] *= CF
                except KeyError:
                    pass
                except IndexError:
                    pass 
                try:
                    self._datadict[sample][code]['real_area'] *= CF    
                except KeyError:
                    pass
        return

    def norm_area(self):
        norm = self._project.info.norm_method
        if norm == 'tic':
            print('Normalization against TIC')
            self.norm_tic()
        elif norm == 'sum':
            print('Normalization against sum')
            self.norm_sum()
        elif norm:
            print('Normalization against {0}'.format(norm))
            code = amdis.correct_code(norm)
            if code in self._project.library:
                self.norm_std(code)
            else:
                print('ERROR: code for internal standard not present')
                print('Change norm_method in pyquan.ini')
                sys.exit(2) 
        if self._CFnorm:
            for sample in  self._project.runlist:
                for code in self._datadict[sample]:
                    self._datadict[sample][code]['area_norm'] =\
                    self._datadict[sample][code]['area'] / self._CFnorm[sample] 
        return

    def norm_std(self, code):
        self._CFnorm = {}
        for samples in self._project.runlist:
            try:
                self._CFnorm[sample] = self._datadict[sample][code]['area']
            except KeyError:
                print('ERROR: Internal standard not present in all samples')
                print('Choose different standard or method in pyquan.ini')
                sys.exit(2)
        return
    
    def norm_sum(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            area = 0.
            for code in self._datadict[sample]:
                area += self._datadict[sample][code]['area']
            self._CFnorm[sample] = area
        return

    def norm_tic(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            self._CFnorm[sample] = sum(self._TIC[sample]) - \
                                   sum(self._baseline[sample])
        return            


class WriteFiles(object):
    def __init__(self, project):
        self._makeline = project.csv.make_line
        self._RTfile = project.path.RT_file
        self._fitfile = project.path.fit_file
        self._areafile = project.path.area_norm_file
        self._codelist = []
        self._samplelist = []

    def write_RT(self, RTdict):
        self.writedata('RT', RTdict, self._RTfile)
        return

    def write_fit(self, fitdict):
        self.writedata('fit', fitdict, self._fitfile)
        return

    def write_area(self, areadict):
        self.writedata('area_norm', areadict, self._areafile)
        return

    def writedata(self, item, datadict, filename):
        with open(filename, 'w') as f:
            f.write(self.header(item))
            for code in self._codelist:
                datalist = [code]
                for sample in self._samplelist:
                    datalist.append(datadict[code].get(sample, 'ND'))
                f.write(self._makeline(datalist))
        return

    def header(self, item):
        headerlist = [item] + self._samplelist
        return self._makeline(headerlist)

class Normalize(object):
    def __init__(self, project):
        print('Collect data')
        sys.stdout.flush()
        self._project = project
        self._mzratio = mzratio.CF(project)
        print('Write output files')
        sys.stdout.flush()

    def CF(self, code):
        return self._mzratio.CF(code)

    def writedata(self):
        writefiles = WriteFiles(self._project)
        with datafiles.HDF5(self._project.path.hdf5) as f:
            f.get_project_data()
            writefiles._samplelist = f.samplelist
            writefiles._codelist = f.codelist
            writefiles.write_RT(f.RTdict)
            writefiles.write_fit(f.fitdict)
            self._areadict = f.areadict
        self.normalize()
        writefiles.write_area(self._areadict)
        return

    def normalize(self):
        norm = self._project.info.norm_method
        if norm == 'tic':
            print('Normalization against TIC')
            self.norm_tic()
        elif norm == 'sum':
            print('Normalization against sum')
            self.norm_sum()
        elif norm:
            print('Normalization against {0}'.format(norm))
            code = amdis.correct_code(norm)
            if code in self._project.library:
                self.norm_std(code)
            else:
                print('ERROR: code for internal standard not present')
                print('Change norm_method in pyquan.ini')
                sys.exit(2) 
        if self._CFnorm:
            for code in  self._areadict:
                for sample in self._areadict[code]:
                    try:
                        self._areadict[code][sample] /=self._CFnorm[sample]
                    except TypeError:
                        pass
        return

    def norm_std(self, code):
        self._CFnorm = {}
        for samples in self._project.runlist:
            try:
                self._CFnorm[sample] = self._areadict[sample][code]
            except KeyError:
                print('ERROR: Internal standard not present in all samples')
                print('Choose different standard or method in pyquan.ini')
                sys.exit(2)
        return
    
    def norm_sum(self):
        self._CFnorm = dict.fromkeys(self._project.runlist, 0.)
        for code in self._areadict:
            for sample, area in self._areadict[code].items():
                try:
                    self._CFnorm[sample] += area
                except TypeError:
                    pass
        return

    def norm_tic(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            self._CFnorm[sample] = sum(self._TIC[sample]) - \
                                   sum(self._baseline[sample])
        return            

       

    def makefigures(self):
        print('Create output figures')
        sys.stdout.flush()
        with datafiles.HDF5(self._project.path.hdf5) as f:
            for sample in self._project.runlist:
                figures = normfigures.NormFigures(self._project, sample, self._data)
                figures.make_figures()
        print('\nFinished')
        return

def main(project_name=None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    project = proj.Project(project_name)
    project.read_library()
    normalize = Normalize(project)
    normalize.writedata()
    normalize.makefigures()
    return 0 

if __name__=='__main__':
    status = main()
    sys.exit(status)    
