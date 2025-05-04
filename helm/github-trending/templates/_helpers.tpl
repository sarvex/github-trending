{{/*
Expand the name of the chart.
*/}}
{{- define "github-trending.fullname" -}}
{{- printf "%s" .Release.Name -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "github-trending.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "github-trending.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "github-trending.selectorLabels" -}}
app.kubernetes.io/name: {{ include "github-trending.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
