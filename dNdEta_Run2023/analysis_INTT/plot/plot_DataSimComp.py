#! /usr/bin/env python
from optparse import OptionParser
import sys
import os
import datetime
from array import *
from ROOT import *
import numpy
import math
import glob
from plotUtil import *

gROOT.LoadMacro('./sPHENIXStyle/sPhenixStyle.C')
gROOT.ProcessLine('SetsPhenixStyle()')
gROOT.SetBatch(True)

def Draw_1Dhist_datasimcomp(hdata, hsims, gpadmargin, norm, logy, ymaxscale, XaxisName, Ytitle_unit, prelim, simlegtex, outname):
    hsimcolor = colorset(len(hsims))

    hdata.Sumw2()
    for hsim in hsims:
        hsim.Sumw2()

    binwidth = hdata.GetXaxis().GetBinWidth(1)

    if norm == 'unity':
        hdata.Scale(1. / hdata.Integral(-1, -1))
        for hsim in hsims:
            hsim.Scale(1. / hsim.Integral(-1, -1))
    elif norm == 'data':
        for hsim in hsims:
            hsim.Scale(hdata.Integral(-1, -1) / hsim.Integral(-1, -1))
    else:
        if norm != 'none':
            print('Invalid normalization option: {}'.format(norm))
            sys.exit(1)
    
    # Get the maximum bin content 
    maxbincontent = max(hdata.GetMaximum(), hsim.GetMaximum())

    c = TCanvas('c', 'c', 800, 700)
    if logy:
        c.SetLogy()
    c.cd()
    gPad.SetRightMargin(gpadmargin[0])
    gPad.SetTopMargin(gpadmargin[1])
    gPad.SetLeftMargin(gpadmargin[2])
    gPad.SetBottomMargin(gpadmargin[3])
    
    for i, hsim in enumerate(hsims):
        if i == 0:
            if norm == 'unity':
                if Ytitle_unit == '':
                    hsim.GetYaxis().SetTitle(
                        'Normalized entries / ({:g})'.format(binwidth))
                else:
                    hsim.GetYaxis().SetTitle(
                        'Normalized entries / ({:g} {unit})'.format(binwidth, unit=Ytitle_unit))
            else:
                if Ytitle_unit == '':
                    hsim.GetYaxis().SetTitle('Entries / ({:g})'.format(binwidth))
                else:
                    hsim.GetYaxis().SetTitle(
                        'Entries / ({:g} {unit})'.format(binwidth, unit=Ytitle_unit))

            if logy:
                hsim.GetYaxis().SetRangeUser(hsim.GetMinimum(0)*0.5, (hsim.GetMaximum()) * ymaxscale)
            else:
                hsim.GetYaxis().SetRangeUser(0., (hsim.GetMaximum()) * ymaxscale)

            hsim.GetXaxis().SetTitle(XaxisName)
            hsim.GetXaxis().SetTitleOffset(1.1)
            hsim.GetYaxis().SetTitleOffset(1.35)
            hsim.SetLineColor(TColor.GetColor(hsimcolor[i]))
            hsim.SetLineWidth(2)
            hsim.SetMarkerSize(0)
            hsim.Draw('histe')
        else:
            hsim.SetLineColor(TColor.GetColor(hsimcolor[i]))
            hsim.SetLineWidth(2)
            hsim.SetMarkerSize(0)
            hsim.Draw('histe same')

    hdata.SetMarkerStyle(20)
    hdata.SetMarkerSize(1)
    hdata.SetMarkerColor(1)
    hdata.SetLineColor(1)
    hdata.SetLineWidth(2)
    hdata.Draw('same PE1')
    shift = 0.45 if prelim else 0.54
    legylow = 0.2 + 0.04 * (len(hsims) - 1)
    leg = TLegend((1-RightMargin)-shift, (1-TopMargin)-legylow,
                  (1-RightMargin)-0.1, (1-TopMargin)-0.03)
    leg.SetTextSize(0.04)
    leg.SetFillStyle(0)
    # prelimtext = 'Preliminary' if prelim else 'Work-in-progress'
    prelimtext = 'Preliminary' if prelim else 'Internal'
    leg.AddEntry('', '#it{#bf{sPHENIX}} '+prelimtext, '')
    leg.AddEntry('', 'Au+Au #sqrt{s_{NN}}=200 GeV', '')
    leg.AddEntry(hdata, 'Data', "PE1");
    for i, lt in enumerate(simlegtex):
        leg.AddEntry(hsims[i], lt, "le");
    leg.Draw()
    c.RedrawAxis()
    c.Draw()
    c.SaveAs(outname+'.pdf')
    c.SaveAs(outname+'.png')
    if(c):
        c.Close()
        gSystem.ProcessEvents()
        del c
        c = 0

# Customized version for data-sim comparison with 2 data sets
def Draw_1Dhist_datasimcomp_v2(hdata1, hdata2, hsim, gpadmargin, norm, logy, ymaxscale, XaxisName, Ytitle_unit, legtext, prelim, outname):
    hdata1.Sumw2()
    hdata2.Sumw2()
    hsim.Sumw2()
    binwidth = hdata1.GetXaxis().GetBinWidth(1)
    if norm == 'unity':
        hdata1.Scale(1. / hdata1.Integral(-1, -1))
        hdata2.Scale(1. / hdata2.Integral(-1, -1))
        hsim.Scale(1. / hsim.Integral(-1, -1))
    elif norm == 'data':
        hsim.Scale((hdata1.Integral(-1, -1)+hdata2.Integral(-1, -1)) / hsim.Integral(-1, -1))
    else:
        if norm != 'none':
            print('Invalid normalization option: {}'.format(norm))
            sys.exit(1)

    c = TCanvas('c', 'c', 800, 700)
    if logy:
        c.SetLogy()
    c.cd()
    gPad.SetRightMargin(gpadmargin[0])
    gPad.SetTopMargin(gpadmargin[1])
    gPad.SetLeftMargin(gpadmargin[2])
    gPad.SetBottomMargin(gpadmargin[3])
    if norm == 'unity':
        if Ytitle_unit == '':
            hsim.GetYaxis().SetTitle(
                'Normalized entries / ({:g})'.format(binwidth))
        else:
            hsim.GetYaxis().SetTitle(
                'Normalized entries / ({:g} {unit})'.format(binwidth, unit=Ytitle_unit))
    else:
        if Ytitle_unit == '':
            hsim.GetYaxis().SetTitle('Entries / ({:g})'.format(binwidth))
        else:
            hsim.GetYaxis().SetTitle(
                'Entries / ({:g} {unit})'.format(binwidth, unit=Ytitle_unit))

    if logy:
        hsim.GetYaxis().SetRangeUser(hsim.GetMinimum(0)*0.5, (hsim.GetMaximum()) * ymaxscale)
    else:
        hsim.GetYaxis().SetRangeUser(0., (hsim.GetMaximum()) * ymaxscale)
    hsim.GetXaxis().SetTitle(XaxisName)
    hsim.GetXaxis().SetTitleOffset(1.1)
    hsim.GetYaxis().SetTitleOffset(1.35)
    hsim.SetLineColor(1)
    hsim.SetLineWidth(2)
    hsim.Draw('hist')
    hdata1.SetMarkerStyle(20)
    hdata1.SetMarkerSize(1)
    hdata1.SetMarkerColor(TColor.GetColor('#0B60B0'))
    hdata1.SetLineColor(TColor.GetColor('#0B60B0'))
    hdata1.SetLineWidth(2)
    hdata1.Draw('same PE1')
    hdata2.SetMarkerStyle(20)
    hdata2.SetMarkerSize(1)
    hdata2.SetMarkerColor(TColor.GetColor('#D24545'))
    hdata2.SetLineColor(TColor.GetColor('#D24545'))
    hdata2.SetLineWidth(2)
    hdata2.Draw('same PE1')
    shift = 0.45 if prelim else 0.52
    leg = TLegend((1-RightMargin)-shift, (1-TopMargin)-0.25,
                    (1-RightMargin)-0.1, (1-TopMargin)-0.03)
    leg.SetTextSize(0.04)
    leg.SetFillStyle(0)
    # prelimtext = 'Preliminary' if prelim else 'Work-in-progress'
    prelimtext = 'Preliminary' if prelim else 'Internal'
    leg.AddEntry('', '#it{#bf{sPHENIX}} '+prelimtext, '')
    leg.AddEntry('', 'Au+Au #sqrt{s_{NN}}=200 GeV', '')
    leg.AddEntry(hdata1, legtext[0], "PE1");
    leg.AddEntry(hdata2, legtext[1], "PE1");
    leg.AddEntry(hsim, legtext[2], "l");
    leg.Draw()
    c.RedrawAxis()
    c.Draw()
    c.SaveAs(outname+'.pdf')
    c.SaveAs(outname+'.png')
    if(c):
        c.Close()
        gSystem.ProcessEvents()
        del c
        c = 0

# comparae data and (one of the) simulation
def Draw_2Dhist_datasimcomp(hdata, hsim, logz, norm, rmargin, XaxisName, YaxisName, outname):
    if norm == 'unity':
        hdata.Scale(1. / hdata.Integral(-1, -1, -1, -1))
        hsim.Scale(1. / hsim.Integral(-1, -1, -1, -1))
    elif norm == 'data':
        hsim.Scale(hdata.Integral(-1, -1, -1, -1) / hsim.Integral(-1, -1, -1, -1))
    else:
        if norm != 'none':
            print('Invalid normalization option: {}'.format(norm))
            sys.exit(1)
    
    c = TCanvas('c', 'c', 800, 700)
    if logz:
        c.SetLogz()
    c.cd()
    gPad.SetRightMargin(rmargin)
    gPad.SetTopMargin(TopMargin)
    gPad.SetLeftMargin(LeftMargin)
    gPad.SetBottomMargin(BottomMargin)
    hdata.GetXaxis().SetTitle(XaxisName)
    hdata.GetYaxis().SetTitle(YaxisName)
    hdata.GetXaxis().SetTickSize(TickSize)
    hdata.GetYaxis().SetTickSize(TickSize)
    hdata.GetXaxis().SetTitleSize(AxisTitleSize)
    hdata.GetYaxis().SetTitleSize(AxisTitleSize)
    hdata.GetXaxis().SetLabelSize(AxisLabelSize)
    hdata.GetYaxis().SetLabelSize(AxisLabelSize)
    hdata.GetXaxis().SetTitleOffset(1.1)
    hdata.GetYaxis().SetTitleOffset(1.3)
    hdata.GetZaxis().SetLabelSize(AxisLabelSize)
    hdata.SetLineColor(kBlack)
    hdata.SetLineWidth(1)
    hdata.Draw('box')
    hsim.SetLineColorAlpha(kRed, 0.5)
    hsim.SetLineWidth(1)
    hsim.Draw('box same')
    c.RedrawAxis()
    c.Draw()
    c.SaveAs(outname+'.pdf')
    c.SaveAs(outname+'.png')
    if(c):
        c.Close()
        gSystem.ProcessEvents()
        del c
        c = 0


if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog ver [options -h]')
    parser.add_option('-d', '--datahistdir', dest='datahistdir', type='string', default='/sphenix/user/hjheng/TrackletAna/analysis_INTT/plot/hists/data_run20869/Hists_RecoTracklets_merged.root', help='Histogram file name (data)')
    parser.add_option('-s', '--simhistdir', action='append', dest='simhistdir', type='string', help='Histogram file name (simulation). Example: /sphenix/user/hjheng/TrackletAna/analysis_INTT/plot/hists/ana382_zvtx-20cm_dummyAlignParams/Hists_RecoTracklets_merged.root')
    parser.add_option('-l', '--simlegtext', action='append', dest='simlegtext', type='string', help='Legend text for simulation. Example: HIJING/EPOS/AMPT)')
    parser.add_option('-p', '--plotdir', dest='plotdir', type='string', default='ana382_zvtx-20cm_dummyAlignParams', help='Plot directory')

    (opt, args) = parser.parse_args()

    print('opt: {}'.format(opt))

    datahistdir = opt.datahistdir
    simhistdir = opt.simhistdir
    simlegtext = opt.simlegtext
    plotdir = opt.plotdir

    if os.path.isfile("{}/hists_merged.root".format(datahistdir)):
        os.system("rm {}/hists_merged.root".format(datahistdir))
        os.system("hadd {}/hists_merged.root {}/hists_*.root".format(datahistdir, datahistdir))
    else:
        os.system("hadd {}/hists_merged.root {}/hists_*.root".format(datahistdir, datahistdir))
    
    for simhistd in simhistdir:
        if os.path.isfile("{}/hists_merged.root".format(simhistd)):
            os.system("rm {}/hists_merged.root".format(simhistd))
            os.system("hadd {}/hists_merged.root {}/hists_*.root".format(simhistd, simhistd))
        else:
            os.system("hadd {}/hists_merged.root {}/hists_*.root".format(simhistd, simhistd))

    os.makedirs('./DataSimComp/{}'.format(plotdir), exist_ok=True)

    hM_NClusLayer1_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_NClusLayer1')
    hM_NClusLayer1_clusADCgt35_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_NClusLayer1_clusADCgt35')
    hM_NTklclusLayer1_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_NTklclusLayer1')
    hM_NPrototkl_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_NPrototkl')
    hM_NRecotkl_Raw_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_NRecotkl_Raw')
    hM_dEta_reco_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dEta_reco') 
    hM_dEta_reco_altrange_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dEta_reco_altrange')
    hM_dPhi_reco_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco')
    hM_dPhi_reco_altrange_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_altrange')
    hM_dPhi_reco_Centrality_0to10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_0to10')
    hM_dPhi_reco_Centrality_10to20_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_10to20')
    hM_dPhi_reco_Centrality_20to30_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_20to30')
    hM_dPhi_reco_Centrality_30to40_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_30to40')
    hM_dPhi_reco_Centrality_40to50_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_40to50')
    hM_dPhi_reco_Centrality_50to60_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_50to60')
    hM_dPhi_reco_Centrality_60to70_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_60to70')
    hM_dPhi_reco_Centrality_70to80_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_70to80')
    hM_dPhi_reco_Centrality_80to90_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_80to90')
    hM_dPhi_reco_Centrality_90to100_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_90to100')
    hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75')
    hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10')
    hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10')
    hM_dR_reco_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_dR_reco')
    hM_Eta_reco_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_Eta_reco')
    hM_Phi_reco_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_Phi_reco')
    hM_RecoPVz_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_RecoPVz')
    hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10')
    hM_MBDChargeAsymm_Le0p75_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_MBDChargeAsymm_Le0p75')
    hM_MBDChargeAsymm_Le0p75_VtxZm30tom10_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_MBDChargeAsymm_Le0p75_VtxZm30tom10')
    hM_clusphi_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_clusphi')
    hM_cluseta_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_cluseta')
    hM_clusphisize_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_clusphisize')
    hM_cluseta_clusphisize_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_cluseta_clusphisize')
    hM_clusphi_clusphisize_data = GetHistogram("{}/hists_merged.root".format(datahistdir), 'hM_clusphi_clusphisize')

    l_hM_NClusLayer1_sim = []
    l_hM_NClusLayer1_clusADCgt35_sim = []
    l_hM_NTklclusLayer1_sim = []
    l_hM_NPrototkl_sim = []
    l_hM_NRecotkl_Raw_sim = []
    l_hM_dEta_reco_sim = []
    l_hM_dEta_reco_altrange_sim = []
    l_hM_dPhi_reco_sim = []
    l_hM_dPhi_reco_altrange_sim = []
    l_hM_dPhi_reco_Centrality_0to10_sim = []
    l_hM_dPhi_reco_Centrality_10to20_sim = []
    l_hM_dPhi_reco_Centrality_20to30_sim = []
    l_hM_dPhi_reco_Centrality_30to40_sim = []
    l_hM_dPhi_reco_Centrality_40to50_sim = []
    l_hM_dPhi_reco_Centrality_50to60_sim = []
    l_hM_dPhi_reco_Centrality_60to70_sim = []
    l_hM_dPhi_reco_Centrality_70to80_sim = []
    l_hM_dPhi_reco_Centrality_80to90_sim = []
    l_hM_dPhi_reco_Centrality_90to100_sim = []
    l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_sim = []
    l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_dR_reco_sim = []
    l_hM_Eta_reco_sim = []
    l_hM_Phi_reco_sim = []
    l_hM_RecoPVz_sim = []
    l_hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10_sim = []
    l_hM_MBDChargeAsymm_Le0p75_sim = []
    l_hM_MBDChargeAsymm_Le0p75_VtxZm30tom10_sim = []
    l_hM_clusphi_sim = []
    l_hM_cluseta_sim = []
    l_hM_clusphisize_sim = []
    l_hM_cluseta_clusphisize_sim = []
    l_hM_clusphi_clusphisize_sim = []
    for i, simhistd in enumerate(simhistdir):
        l_hM_NClusLayer1_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_NClusLayer1'))
        l_hM_NClusLayer1_clusADCgt35_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_NClusLayer1_clusADCgt35'))
        l_hM_NTklclusLayer1_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_NTklclusLayer1'))
        l_hM_NPrototkl_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_NPrototkl'))
        l_hM_NRecotkl_Raw_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_NRecotkl_Raw'))
        l_hM_dEta_reco_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dEta_reco'))
        l_hM_dEta_reco_altrange_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dEta_reco_altrange'))
        l_hM_dPhi_reco_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco'))
        l_hM_dPhi_reco_altrange_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_altrange'))
        l_hM_dPhi_reco_Centrality_0to10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_0to10'))
        l_hM_dPhi_reco_Centrality_10to20_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_10to20'))
        l_hM_dPhi_reco_Centrality_20to30_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_20to30'))
        l_hM_dPhi_reco_Centrality_30to40_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_30to40'))
        l_hM_dPhi_reco_Centrality_40to50_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_40to50'))
        l_hM_dPhi_reco_Centrality_50to60_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_50to60'))
        l_hM_dPhi_reco_Centrality_60to70_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_60to70'))
        l_hM_dPhi_reco_Centrality_70to80_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_70to80'))
        l_hM_dPhi_reco_Centrality_80to90_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_80to90'))
        l_hM_dPhi_reco_Centrality_90to100_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_90to100'))
        l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75'))
        l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_dR_reco_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_dR_reco'))
        l_hM_Eta_reco_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_Eta_reco'))
        l_hM_Phi_reco_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_Phi_reco'))
        l_hM_RecoPVz_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_RecoPVz'))
        l_hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10'))
        l_hM_MBDChargeAsymm_Le0p75_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_MBDChargeAsymm_Le0p75'))
        l_hM_MBDChargeAsymm_Le0p75_VtxZm30tom10_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_MBDChargeAsymm_Le0p75_VtxZm30tom10'))
        l_hM_clusphi_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_clusphi'))
        l_hM_cluseta_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_cluseta'))
        l_hM_clusphisize_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_clusphisize'))
        l_hM_cluseta_clusphisize_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_cluseta_clusphisize'))
        l_hM_clusphi_clusphisize_sim.append(GetHistogram("{}/hists_merged.root".format(simhistd), 'hM_clusphi_clusphisize'))

    # Draw_1Dhist_datasimcomp(hdata, hsim, norm, logy, ymaxscale, XaxisName, Ytitle_unit, prelim, outname)
    hM_NClusLayer1_data.GetXaxis().SetMaxDigits(2)
    for hM_NClusLayer1_sim in l_hM_NClusLayer1_sim:
        hM_NClusLayer1_sim.GetXaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_NClusLayer1_data, l_hM_NClusLayer1_sim, [0.1,0.08,0.15,0.13], 'data', True, 10, 'Number of clusters (inner)', '', False, simlegtext, './DataSimComp/{}/NClusLayer1'.format(plotdir))

    hM_NClusLayer1_clusADCgt35_data.GetXaxis().SetMaxDigits(2)
    for hM_NClusLayer1_clusADCgt35_sim in l_hM_NClusLayer1_clusADCgt35_sim:
        hM_NClusLayer1_clusADCgt35_sim.GetXaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_NClusLayer1_clusADCgt35_data, l_hM_NClusLayer1_clusADCgt35_sim, [0.1,0.08,0.15,0.13], 'data', True, 10, 'Number of clusters (inner)', '', False, simlegtext, './DataSimComp/{}/NClusLayer1_clusADCgt35'.format(plotdir))    
    
    
    hM_NTklclusLayer1_data.GetXaxis().SetMaxDigits(2)
    for hM_NTklclusLayer1_sim in l_hM_NTklclusLayer1_sim:
        hM_NTklclusLayer1_sim.GetXaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_NTklclusLayer1_data, l_hM_NTklclusLayer1_sim, [0.1,0.08,0.15,0.13], 'data', True, 10, 'Number of tracklet clusters (inner)', '', False, simlegtext, './DataSimComp/{}/NTklClusLayer1'.format(plotdir))
    
    hM_NPrototkl_data.GetXaxis().SetMaxDigits(2)
    for hM_NPrototkl_sim in l_hM_NPrototkl_sim:
        hM_NPrototkl_sim.GetXaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_NPrototkl_data, l_hM_NPrototkl_sim, [0.1,0.08,0.15,0.13], 'data', True, 3, 'Number of proto-tracklets', '', False, simlegtext, './DataSimComp/{}/NProtoTracklets'.format(plotdir))
    
    hM_NRecotkl_Raw_data.GetXaxis().SetMaxDigits(2)
    for hM_NRecotkl_Raw_sim in l_hM_NRecotkl_Raw_sim:
        hM_NRecotkl_Raw_sim.GetXaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_NRecotkl_Raw_data, l_hM_NRecotkl_Raw_sim, [0.1,0.08,0.15,0.13], 'data', True, 10, 'Number of reco-tracklets', '', False, simlegtext, './DataSimComp/{}/NRecoTracklets_Raw'.format(plotdir))
    
    Draw_1Dhist_datasimcomp(hM_RecoPVz_data, l_hM_RecoPVz_sim, [0.1,0.08,0.15,0.13], 'data', True, 250, 'Reco PV z [cm]', 'cm', False, simlegtext, './DataSimComp/{}/RecoPVz'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_RecoPVz_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', False, 1.5, 'Reco PV z [cm]', 'cm', False, simlegtext, './DataSimComp/{}/RecoPVz_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_MBDChargeAsymm_Le0p75_data, l_hM_MBDChargeAsymm_Le0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 15, 'MBD charge asymmetry', '', False, simlegtext, './DataSimComp/{}/MBDChargeAsymm'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_MBDChargeAsymm_Le0p75_VtxZm30tom10_data, l_hM_MBDChargeAsymm_Le0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 15, 'MBD charge asymmetry', '', False, simlegtext, './DataSimComp/{}/MBDChargeAsymm_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_clusphi_data, l_hM_clusphi_sim, [0.1,0.08,0.15,0.13], 'data', False, 1.8, 'Cluster #phi', '', False, simlegtext, './DataSimComp/{}/Cluster_Phi'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_cluseta_data, l_hM_cluseta_sim, [0.1,0.08,0.15,0.13], 'data', False, 1.8, 'Cluster #eta', '', False, simlegtext, './DataSimComp/{}/Cluster_Eta'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_clusphisize_data, l_hM_clusphisize_sim, [0.1,0.08,0.15,0.13], 'data', True, 10, 'Cluster #phi size', '', False, simlegtext, './DataSimComp/{}/Cluster_PhiSize'.format(plotdir))

    Draw_1Dhist_datasimcomp(hM_dEta_reco_data, l_hM_dEta_reco_sim, [0.08,0.08,0.15,0.13], 'data', True, 250, 'Reco-tracklet #Delta#eta', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dEta'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dEta_reco_altrange_data, l_hM_dEta_reco_altrange_sim, [0.08,0.08,0.15,0.13], 'data', True, 250, 'Reco-tracklet #Delta#eta', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dEta_altrange'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_data, l_hM_dPhi_reco_sim, [0.08,0.08,0.15,0.13], 'data', True, 500, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi'.format(plotdir))
    
    hM_dPhi_reco_altrange_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_0to10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_10to20_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_20to30_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_30to40_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_40to50_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_50to60_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_60to70_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_70to80_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_80to90_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_90to100_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_data.GetXaxis().SetMaxDigits(2)
    for i in range(len(l_hM_dPhi_reco_altrange_sim)):
        l_hM_dPhi_reco_altrange_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_0to10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_10to20_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_20to30_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_30to40_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_40to50_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_50to60_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_60to70_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_70to80_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_80to90_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_90to100_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_sim[i].GetXaxis().SetMaxDigits(2)
        
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_altrange_data, l_hM_dPhi_reco_altrange_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_altrange'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_0to10_data, l_hM_dPhi_reco_Centrality_0to10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_0to10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_10to20_data, l_hM_dPhi_reco_Centrality_10to20_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_10to20'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_20to30_data, l_hM_dPhi_reco_Centrality_20to30_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_20to30'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_30to40_data, l_hM_dPhi_reco_Centrality_30to40_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_30to40'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_40to50_data, l_hM_dPhi_reco_Centrality_40to50_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_40to50'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_50to60_data, l_hM_dPhi_reco_Centrality_50to60_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_50to60'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_60to70_data, l_hM_dPhi_reco_Centrality_60to70_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_60to70'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_70to80_data, l_hM_dPhi_reco_Centrality_70to80_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_70to80'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_80to90_data, l_hM_dPhi_reco_Centrality_80to90_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_80to90'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_90to100_data, l_hM_dPhi_reco_Centrality_90to100_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_90to100'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_0to10_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_10to20_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_20to30_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_30to40_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_40to50_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_50to60_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_60to70_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_70to80_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_80to90_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_data, l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_90to100_MBDAsymLe0p75'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_0to10_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_10to20_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_20to30_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_30to40_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_40to50_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_50to60_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_60to70_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_70to80_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_80to90_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_data, l_hM_dPhi_reco_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10_sim, [0.1,0.08,0.15,0.13], 'data', True, 150, 'Reco-tracklet #Delta#phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dPhi_Centrality_90to100_MBDAsymLe0p75_VtxZm30tom10'.format(plotdir))
    
    Draw_1Dhist_datasimcomp(hM_dR_reco_data, l_hM_dR_reco_sim, [0.08,0.08,0.15,0.13], 'data', True, 3, 'Reco-tracklet #DeltaR', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_dR'.format(plotdir))
    Draw_1Dhist_datasimcomp(hM_Eta_reco_data, l_hM_Eta_reco_sim, [0.08,0.08,0.15,0.13], 'data', False, 1.8, 'Reco-tracklet #eta', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_Eta'.format(plotdir))
    for hM_Phi_reco_sim in l_hM_Phi_reco_sim:
        hM_Phi_reco_sim.GetYaxis().SetMaxDigits(2)
    Draw_1Dhist_datasimcomp(hM_Phi_reco_data, l_hM_Phi_reco_sim, [0.08,0.08,0.15,0.13], 'data', False, 1.8, 'Reco-tracklet #phi', '', False, simlegtext, './DataSimComp/{}/RecoTracklet_Phi'.format(plotdir))
    
    # Draw_2Dhist_datasimcomp(hdata, hsim, logz, norm, rmargin, XaxisName, YaxisName, outname)
    Draw_2Dhist_datasimcomp(hM_cluseta_clusphisize_data, l_hM_cluseta_clusphisize_sim[0], False, 'data', 0.1, 'Cluster #eta', 'Cluster #phi size', './DataSimComp/{}/ClusEta_ClusPhiSize'.format(plotdir))
    Draw_2Dhist_datasimcomp(hM_clusphi_clusphisize_data, l_hM_clusphi_clusphisize_sim[0], False, 'data', 0.1, 'Cluster #phi', 'Cluster #phi size', './DataSimComp/{}/ClusPhi_ClusPhiSize'.format(plotdir))

