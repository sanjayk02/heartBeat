import React, { useMemo, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
} from "@material-ui/core";
import {
  AssetRowProps,
  AssetsDataTableProps,
  Colors,
  Column,
  RecordTableHeadProps,
} from "./types";
import { useFetchAssetReviewInfos, useFetchAssetThumbnails } from "./hooks";
import SortDropdown from "./SortDropdown";
import { getSortedAssets } from "../utils/sortAssets"; // adjust path if needed

// ----------------- PHASES / STATUS / COLUMNS -----------------
const ASSET_PHASES: { [key: string]: Colors } = {
  mdl: { lineColor: "#3295fd", backgroundColor: "#354d68" },
  rig: { lineColor: "#c061fd", backgroundColor: "#5e3568" },
  bld: { lineColor: "#fc2f8c", backgroundColor: "#5a0028" },
  dsn: { lineColor: "#98f2fb", backgroundColor: "#045660" },
  ldv: { lineColor: "#fe5cff", backgroundColor: "#683566" },
};

type Status = Readonly<{
  displayName: string;
  color: string;
}>;

const APPROVAL_STATUS: { [key: string]: Status } = {
  check: { displayName: "Check", color: "#ca25ed" },
  clientReview: { displayName: "Client Review", color: "#005fbd" },
  dirReview: { displayName: "Dir Review", color: "#007fff" },
  epdReview: { displayName: "EPD Review", color: "#4fa7ff" },
  clientOnHold: { displayName: "Client On Hold", color: "#d69b00" },
  dirOnHold: { displayName: "Dir On Hold", color: "#ffcc00" },
  epdOnHold: { displayName: "EPD On Hold", color: "#ffdd55" },
  execRetake: { displayName: "Exec Retake", color: "#a60000" },
  clientRetake: { displayName: "Client Retake", color: "#c60000" },
  dirRetake: { displayName: "Dir Retake", color: "#ff0000" },
  epdRetake: { displayName: "EPD Retake", color: "#ff4f4f" },
  clientApproved: { displayName: "Client Approved", color: "#1d7c39" },
  dirApproved: { displayName: "Dir Approved", color: "#27ab4f" },
  epdApproved: { displayName: "EPD Approved", color: "#5cda82" },
  other: { displayName: "Other", color: "#9a9a9a" },
  omit: { displayName: "Omit", color: "#646464" },
};

const WORK_STATUS: { [key: string]: Status } = {
  check: { displayName: "Check", color: "#e287f5" },
  cgsvOnHold: { displayName: "CGSV On Hold", color: "#ffdd55" },
  svOnHold: { displayName: "SV On Hold", color: "#ffe373" },
  leadOnHold: { displayName: "Lead On Hold", color: "#fff04f" },
  cgsvRetake: { displayName: "CGSV Retake", color: "#ff4f4f" },
  svRetake: { displayName: "SV Retake", color: "#ff8080" },
  leadRetake: { displayName: "Lead Retake", color: "#ffbbbb" },
  cgsvApproved: { displayName: "CGSV Approved", color: "#5cda82" },
  svApproved: { displayName: "SV Approved", color: "#83e29f" },
  leadApproved: { displayName: "Lead Approved", color: "#b9eec9" },
  svOther: { displayName: "SV Other", color: "#9a9a9a" },
  leadOther: { displayName: "Lead Other", color: "#dbdbdb" },
};

const columns: Column[] = [
  { id: "thumbnail", label: "Thumbnail" },
  { id: "group_1_name", label: "Name" },
  { id: "mdl_work_status", label: "MDL WORK", colors: ASSET_PHASES["mdl"] },
  { id: "mdl_approval_status", label: "MDL APPR", colors: ASSET_PHASES["mdl"] },
  { id: "mdl_submitted_at", label: "MDL Submitted At", colors: ASSET_PHASES["mdl"] },
  { id: "rig_work_status", label: "RIG WORK", colors: ASSET_PHASES["rig"] },
  { id: "rig_approval_status", label: "RIG APPR", colors: ASSET_PHASES["rig"] },
  { id: "rig_submitted_at", label: "RIG Submitted At", colors: ASSET_PHASES["rig"] },
  { id: "bld_work_status", label: "BLD WORK", colors: ASSET_PHASES["bld"] },
  { id: "bld_approval_status", label: "BLD APPR", colors: ASSET_PHASES["bld"] },
  { id: "bld_submitted_at", label: "BLD Submitted At", colors: ASSET_PHASES["bld"] },
  { id: "dsn_work_status", label: "DSN WORK", colors: ASSET_PHASES["dsn"] },
  { id: "dsn_approval_status", label: "DSN APPR", colors: ASSET_PHASES["dsn"] },
  { id: "dsn_submitted_at", label: "DSN Submitted At", colors: ASSET_PHASES["dsn"] },
  { id: "ldv_work_status", label: "LDV WORK", colors: ASSET_PHASES["ldv"] },
  { id: "ldv_approval_status", label: "LDV APPR", colors: ASSET_PHASES["ldv"] },
  { id: "ldv_submitted_at", label: "LDV Submitted At", colors: ASSET_PHASES["ldv"] },
  { id: "relation", label: "Relation" },
];

// ----------------- CELL COMPONENT -----------------
type TooltipTableCellProps = {
  tooltipText: string;
  status: Status | undefined;
  leftBorderStyle: string;
  rightBorderStyle: string;
  bottomBorderStyle: string;
};

const MultiLineTooltipTableCell: React.FC<TooltipTableCellProps> = ({
  tooltipText,
  status,
  leftBorderStyle,
  rightBorderStyle,
  bottomBorderStyle = "none",
}) => {
  const [open, setOpen] = React.useState(false);
  const isTooltipTextEmpty = tooltipText && tooltipText.trim().length > 0;

  const handleTooltipClose = () => setOpen(false);
  const handleTooltipOpen = () => setOpen(true);

  const statusText = status ? status.displayName : "-";

  return (
    <TableCell
      style={{
        color: status ? status.color : "",
        fontStyle: tooltipText === "" ? "normal" : "oblique",
        borderLeft: leftBorderStyle,
        borderRight: rightBorderStyle,
        borderBottom: bottomBorderStyle,
      }}
      onClick={isTooltipTextEmpty ? handleTooltipOpen : undefined}
    >
      {isTooltipTextEmpty ? (
        <Tooltip
          title={
            <div style={{ fontSize: "0.8rem", whiteSpace: "pre-wrap" }}>
              {tooltipText}
            </div>
          }
          onClose={handleTooltipClose}
          open={open}
          arrow
        >
          <span>{statusText}</span>
        </Tooltip>
      ) : (
        <span>{statusText}</span>
      )}
    </TableCell>
  );
};

// ----------------- TABLE HEAD -----------------
const RecordTableHead: React.FC<RecordTableHeadProps> = ({ columns }) => {
  return (
    <TableHead>
      <TableRow>
        {columns.map((column) => {
          const borderLineStyle = column.colors
            ? `solid 3px ${column.colors.lineColor}`
            : "none";
          const borderTopStyle = column.colors ? borderLineStyle : "none";
          const borderLeftStyle = column.id.includes("work_status")
            ? borderLineStyle
            : "none";
          const borderRightStyle = column.id.includes("submitted_at")
            ? borderLineStyle
            : "none";
          return (
            <TableCell
              key={column.id}
              style={{
                backgroundColor: column.colors
                  ? column.colors.backgroundColor
                  : "none",
                borderTop: borderTopStyle,
                borderLeft: borderLeftStyle,
                borderRight: borderRightStyle,
              }}
            >
              {column.label}
            </TableCell>
          );
        })}
      </TableRow>
    </TableHead>
  );
};

// ----------------- ASSET ROW -----------------
const AssetRow: React.FC<AssetRowProps> = ({
  asset,
  reviewInfos,
  thumbnails,
  dateTimeFormat,
  isLastRow,
}) => {
  return (
    <TableRow>
      <TableCell>
        {thumbnails[`${asset.name}-${asset.relation}`] ? (
          <img
            src={thumbnails[`${asset.name}-${asset.relation}`]}
            alt={`${asset.name} thumbnail`}
            style={{ width: "100px", height: "auto" }}
          />
        ) : (
          <span>No Thumbnail</span>
        )}
      </TableCell>
      <TableCell>{asset.name}</TableCell>
      {Object.entries(ASSET_PHASES).map(([phase, { lineColor }]) => {
        const reviewInfoName = `${asset.name}-${asset.relation}-${phase}`;
        const info = reviewInfos[reviewInfoName];
        const workStatus: Status | undefined =
          info && WORK_STATUS[info.work_status];
        const approvalStatus: Status | undefined =
          info && APPROVAL_STATUS[info.approval_status];
        const tooltipText: string =
          info && info.review_comments
            .filter((c: any) => c.text !== "")
            .map((c: any) => `${c.language}:\n${c.text}`)
            .join("\n") || "";
        const submittedAt = info ? new Date(info.submitted_at_utc) : null;
        const localTimeText = submittedAt
          ? dateTimeFormat.format(submittedAt)
          : "-";
        const borderLineStyle = `solid 3px ${lineColor}`;

        return (
          <React.Fragment key={`${reviewInfoName}-row`}>
            <MultiLineTooltipTableCell
              tooltipText={tooltipText}
              status={workStatus}
              leftBorderStyle={borderLineStyle}
              rightBorderStyle="none"
              bottomBorderStyle={isLastRow ? borderLineStyle : "none"}
            />
            <MultiLineTooltipTableCell
              tooltipText={tooltipText}
              status={approvalStatus}
              leftBorderStyle="none"
              rightBorderStyle="none"
              bottomBorderStyle={isLastRow ? borderLineStyle : "none"}
            />
            <TableCell
              style={{
                borderLeft: "none",
                borderRight: borderLineStyle,
                borderBottom: isLastRow ? borderLineStyle : "none",
              }}
            >
              {localTimeText}
            </TableCell>
          </React.Fragment>
        );
      })}
      <TableCell>{asset.relation}</TableCell>
    </TableRow>
  );
};

// ----------------- MAIN COMPONENT -----------------
const AssetsDataTable: React.FC<AssetsDataTableProps> = ({
  project,
  assets,
  tableFooter,
  dateTimeFormat,
}) => {
  if (!project) return null;

  const { reviewInfos } = useFetchAssetReviewInfos(project, assets);
  const { thumbnails } = useFetchAssetThumbnails(project, assets);

  // --- Sort state + dropdown options
  const columnsForSort = columns
    .filter((c) => c.id !== "thumbnail")
    .map((c) => ({ id: c.id, label: c.label }));
  const [sortColumn, setSortColumn] = useState<string | null>("group_1_name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc" | null>(
    "asc"
  );

  const sortedAssets = useMemo(() => {
    return getSortedAssets(assets, sortColumn, sortDirection, reviewInfos);
  }, [assets, sortColumn, sortDirection, reviewInfos]);

  return (
    <div>
      {/* Toolbar: SortDropdown at top */}
      <div
        style={{
          marginBottom: 12,
          display: "flex",
          gap: 12,
          alignItems: "center",
        }}
      >
        <SortDropdown
          value={sortColumn || ""}
          direction={(sortDirection as any) || "asc"}
          columns={columnsForSort}
          onChange={(col, dir) => {
            setSortColumn(col);
            setSortDirection(dir);
          }}
          closeOnSelect={false}
        />

        {/* You can keep other toolbar elements here */}
        <div style={{ color: "#ddd" }}>Asset Name filter here</div>
        <div style={{ color: "#ddd" }}>Approval Status</div>
        <div style={{ color: "#ddd" }}>Work Status</div>

        <div style={{ marginLeft: "auto" }}>
          <button
            style={{
              background: "#444",
              color: "#fff",
              padding: "8px 12px",
              borderRadius: 4,
            }}
          >
            RESET
          </button>
        </div>
      </div>

      <Table stickyHeader>
        <RecordTableHead columns={columns} />
        <TableBody>
          {sortedAssets.map((asset: any, index: number) => (
            <AssetRow
              key={`${asset.name}-${asset.relation}-${index}`}
              asset={asset}
              reviewInfos={reviewInfos}
              thumbnails={thumbnails}
              dateTimeFormat={dateTimeFormat}
              isLastRow={index === sortedAssets.length - 1}
            />
          ))}
        </TableBody>
        {tableFooter || null}
      </Table>
    </div>
  );
};

export default AssetsDataTable;
