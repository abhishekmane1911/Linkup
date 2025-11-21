import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertCircle, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { reportService, Report } from '@/services/reportService';
import { useToast } from '@/hooks/use-toast';
import { motion } from 'framer-motion';
import { format } from 'date-fns';

const MyReports = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchMyReports();
  }, []);

  const fetchMyReports = async () => {
    setIsLoading(true);
    try {
      const response = await reportService.getMyReports();
      setReports(response.results);
    } catch (error: any) {
      console.error('Failed to fetch reports:', error);
      toast({
        title: 'Failed to load reports',
        description: error.response?.data?.error || 'Please try again later',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'under_review':
        return <AlertCircle className="w-4 h-4" />;
      case 'resolved':
        return <CheckCircle className="w-4 h-4" />;
      case 'dismissed':
        return <XCircle className="w-4 h-4" />;
      case 'escalated':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'under_review':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'resolved':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'dismissed':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
      case 'escalated':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  const getReportTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      spam: 'Spam',
      harassment: 'Harassment',
      hate_speech: 'Hate Speech',
      violence: 'Violence',
      inappropriate_content: 'Inappropriate Content',
      copyright: 'Copyright Violation',
      fake_news: 'Fake News',
      impersonation: 'Impersonation',
      other: 'Other',
    };
    return labels[type] || type;
  };

  const filteredReports = reports.filter((report) => {
    if (activeTab === 'all') return true;
    return report.status === activeTab;
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">My Reports</h1>
            <p className="text-sm text-muted-foreground">
              Track the status of your submitted reports
            </p>
          </div>
        </div>

        {/* Tabs for filtering */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="under_review">Under Review</TabsTrigger>
            <TabsTrigger value="resolved">Resolved</TabsTrigger>
            <TabsTrigger value="dismissed">Dismissed</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-4 mt-6">
            {isLoading ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : filteredReports.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <AlertCircle className="w-12 h-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground text-center">
                    {activeTab === 'all'
                      ? "You haven't submitted any reports yet"
                      : `No ${activeTab.replace('_', ' ')} reports`}
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredReports.map((report) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg flex items-center gap-2">
                            <span className="capitalize">{report.content_type}</span>
                            <span className="text-muted-foreground">#{report.object_id}</span>
                          </CardTitle>
                          <CardDescription>
                            Reported {format(new Date(report.created_at), 'PPp')}
                          </CardDescription>
                        </div>
                        <Badge
                          variant="outline"
                          className={`flex items-center gap-1 ${getStatusColor(report.status)}`}
                        >
                          {getStatusIcon(report.status)}
                          <span className="capitalize">{report.status.replace('_', ' ')}</span>
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-1">
                          Report Type
                        </p>
                        <Badge variant="secondary">
                          {getReportTypeLabel(report.report_type)}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-1">
                          Description
                        </p>
                        <p className="text-sm">{report.description}</p>
                      </div>
                      {report.status === 'resolved' && report.resolved_at && (
                        <div className="pt-3 border-t">
                          <p className="text-sm text-muted-foreground">
                            Resolved on {format(new Date(report.resolved_at), 'PPp')}
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MyReports;
